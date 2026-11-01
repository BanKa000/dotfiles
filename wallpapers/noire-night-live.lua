-- Live clock for the "Noire Night" wallpaper, recreating the original Wallpaper Engine scene:
-- big spaced weekday (Anurati), date and 24h clock (Quicksand Bold), white with a soft glow.
-- Loaded by mpvpaper through live-wallpaper (mpv option script=...).

local overlay = mp.create_osd_overlay("ass-events")
overlay.res_x, overlay.res_y = 1366, 768   -- coordinates are in video pixels

local DAYS = { "S U N D A Y", "M O N D A Y", "T U E S D A Y", "W E D N E S D A Y",
               "T H U R S D A Y", "F R I D A Y", "S A T U R D A Y" }
local MONTHS = { "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                 "JUL", "AUG", "SEP", "OCT", "NOV", "DEC" }

-- One text line = three ASS layers: wide halo, soft glow, crisp text with a faint glowing edge.
local function glowing(x, y, font, fs, text, extra)
    local base = string.format("{\\an5\\pos(%d,%d)\\fn%s\\fs%.1f%s\\shad0\\1c&HFFFFFF&\\3c&HFFFFFF&",
                               x, y, font, fs, extra or "")
    return {
        base .. string.format("\\bord%.1f\\3a&HE4&\\blur%.1f\\1a&HD0&}", fs * 0.15, fs * 0.5) .. text,
        base .. string.format("\\bord0\\blur%.1f\\1a&H60&}", fs * 0.25) .. text,
        base .. string.format("\\bord%.1f\\3a&HA0&\\blur%.1f\\1a&H00&}", fs * 0.04, fs * 0.05) .. text,
    }
end

local function render()
    local t = os.date("*t")

    local events = {}
    for _, line in ipairs({
        glowing(688, 336, "Anurati", 122, DAYS[t.wday]),
        glowing(683, 410, "Quicksand", 32.5, string.format("%d %s %d", t.day, MONTHS[t.month], t.year), "\\b1"),
        glowing(683, 440, "Quicksand", 29, string.format("-%02d:%02d-", t.hour, t.min), "\\b1"),
    }) do
        for _, ev in ipairs(line) do events[#events + 1] = ev end
    end
    overlay.data = table.concat(events, "\n")
    overlay:update()
end

-- Redraw right after every minute boundary (cheap: the text changes once a minute).
local function schedule()
    mp.add_timeout(60 - os.date("*t").sec + 0.05, function()
        render()
        schedule()
    end)
end

render()
schedule()
