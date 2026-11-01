import QtQuick
import QtQuick.Controls
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1366
    height: 768
    color: "#1a1b26"

    readonly property color fg:     "#c0caf5"
    readonly property color dim:    "#565f89"
    readonly property color accent: "#7aa2f7"
    readonly property color purple: "#bb9af7"
    readonly property color red:    "#f7768e"
    readonly property color yellow: "#e0af68"
    readonly property string font:  "JetBrainsMono Nerd Font"

    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0

    function doLogin() {
        if (password.text.length === 0) return
        status.text = ""
        sddm.login(username.text, password.text, sessionIndex)
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            password.text = ""
            status.text = "неверный пароль"
            shake.start()
            password.forceActiveFocus()
        }
    }

    Image {
        anchors.fill: parent
        source: config.background
        fillMode: Image.PreserveAspectCrop
        asynchronous: false
    }

    // session names, used for the session switcher text
    ListView {
        id: sessions
        width: 1
        height: 1
        opacity: 0
        interactive: false
        cacheBuffer: 10000
        model: sessionModel
        currentIndex: root.sessionIndex
        delegate: Item { property string sname: model.name }
    }

    Column {
        id: center
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -20
        spacing: 0

        Text {
            id: clock
            anchors.horizontalCenter: parent.horizontalCenter
            font.family: root.font
            font.pixelSize: 96
            font.bold: true
            color: root.fg
            text: Qt.formatTime(new Date(), "HH:mm")
        }

        Text {
            id: date
            anchors.horizontalCenter: parent.horizontalCenter
            font.family: root.font
            font.pixelSize: 18
            color: root.accent
            text: {
                var s = new Date().toLocaleDateString(Qt.locale("ru_RU"), "dddd, d MMMM")
                return s.charAt(0).toUpperCase() + s.slice(1)
            }
        }

        Item { width: 1; height: 44 }

        TextField {
            id: username
            anchors.horizontalCenter: parent.horizontalCenter
            width: 240
            horizontalAlignment: TextInput.AlignHCenter
            font.family: root.font
            font.pixelSize: 15
            color: root.fg
            text: userModel.lastUser
            placeholderText: "пользователь"
            placeholderTextColor: root.dim
            background: Item {}
            KeyNavigation.tab: password
            Keys.onReturnPressed: password.forceActiveFocus()
        }

        Item { width: 1; height: 10 }

        TextField {
            id: password
            anchors.horizontalCenter: parent.horizontalCenter
            width: 260
            height: 44
            horizontalAlignment: TextInput.AlignHCenter
            echoMode: TextInput.Password
            passwordCharacter: "•"
            font.family: root.font
            font.pixelSize: 16
            font.letterSpacing: 3
            color: root.fg
            placeholderText: "пароль"
            placeholderTextColor: root.dim
            focus: true
            background: Rectangle {
                radius: height / 2
                color: Qt.rgba(0.102, 0.106, 0.149, 0.8)
                border.width: 2
                border.color: status.text ? root.red
                            : password.activeFocus ? root.accent
                            : Qt.rgba(0.478, 0.635, 0.969, 0.4)
                Behavior on border.color { ColorAnimation { duration: 200 } }
            }
            Keys.onReturnPressed: root.doLogin()
            Keys.onEnterPressed: root.doLogin()
            onTextChanged: if (text) status.text = ""

            SequentialAnimation {
                id: shake
                property real x0: 0
                NumberAnimation { target: password; property: "anchors.horizontalCenterOffset"; to: -10; duration: 50 }
                NumberAnimation { target: password; property: "anchors.horizontalCenterOffset"; to: 10;  duration: 50 }
                NumberAnimation { target: password; property: "anchors.horizontalCenterOffset"; to: -6;  duration: 50 }
                NumberAnimation { target: password; property: "anchors.horizontalCenterOffset"; to: 0;   duration: 50 }
            }
        }

        Item { width: 1; height: 12 }

        Text {
            id: status
            anchors.horizontalCenter: parent.horizontalCenter
            font.family: root.font
            font.pixelSize: 13
            color: root.red
            text: ""
            height: 18
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            font.family: root.font
            font.pixelSize: 13
            color: root.dim
            text: keyboard.layouts.length > 0 ? keyboard.layouts[keyboard.currentLayout].shortName : ""
        }
    }

    // bottom left: session switcher
    Text {
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 24
        font.family: root.font
        font.pixelSize: 14
        color: sessionArea.containsMouse ? root.accent : root.dim
        text: "  " + (sessions.currentItem ? sessions.currentItem.sname : "")
        MouseArea {
            id: sessionArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: root.sessionIndex = (root.sessionIndex + 1) % sessions.count
        }
    }

    // bottom right: power buttons
    Row {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 24
        spacing: 22

        Repeater {
            model: [
                { icon: "", hover: root.purple, enabled: sddm.canSuspend,  act: function() { sddm.suspend() } },
                { icon: "", hover: root.yellow, enabled: sddm.canReboot,   act: function() { sddm.reboot() } },
                { icon: "", hover: root.red,    enabled: sddm.canPowerOff, act: function() { sddm.powerOff() } }
            ]
            delegate: Text {
                visible: modelData.enabled
                font.family: root.font
                font.pixelSize: 20
                color: area.containsMouse ? modelData.hover : root.dim
                text: modelData.icon
                Behavior on color { ColorAnimation { duration: 150 } }
                MouseArea {
                    id: area
                    anchors.fill: parent
                    anchors.margins: -6
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: modelData.act()
                }
            }
        }
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: {
            clock.text = Qt.formatTime(new Date(), "HH:mm")
        }
    }

    Component.onCompleted: password.forceActiveFocus()
}
