load "$NCARG_ROOT/lib/ncarg/nclscripts/contrib/cd_string.ncl"
;------------------------------------------------------------------

function validtime(yyyymmddhh, plus, format)
begin
    time = yyyymmddhh
    year=time/1000000
    month=(time-year*1000000)/10000
    day=(time-(time/10000)*10000)/100
    hr=time-(time/100)*100

    time_hours = cd_inv_calendar(year, month, day, hr, 00, 00, "hours since 1800-01-01 00:00", 0 )
    time_hours= time_hours + plus
    ;time_parts = cd_calendar(time_hours,0))
    ;format = "%D-%c %Y (%HH)"

    stime  = cd_string(time_hours, format)
    return(stime)
end

