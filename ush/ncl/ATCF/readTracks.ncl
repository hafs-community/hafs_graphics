function hourDiff(firsttime, lastime)
begin
  yyyymmddhh = (/firsttime, lastime/)
  yrfrac = yyyymmddhh_to_yyyyfrac(yyyymmddhh, 0)
  return(tointeger((yrfrac(1)-yrfrac(0))*24*360))
end

function getTimeHour(time)
begin
    year=time/1000000
    month=(time-year*1000000)/10000
    day=(time-(time/10000)*10000)/100
    hr=time-(time/100)*100

    time_hours = cd_inv_calendar(year, month, day, hr, 00, 00, "hours since 1800-01-01 00:00", 0 )
    return(time_hours)
end

function getStartDate( fileName, type)
;;;;;;; get startdate from adeck file
begin
    startDate = -1
;    if (fileexists(fileName)) then
	    if strlen(type) .lt. 4 then
        	type = " " + type
	    end if
	    if strlen(type) .lt. 5 then
        	type = " " + type
	    end if
	    data = asciiread(fileName,-1,"string")
	    lineNumber = dimsizes(data)
	    do line = 0,lineNumber-1
        	words=str_split(data(line),",")
	        if (dimsizes(words) .gt. 7) then
        	    date = stringtointeger(words(2))
	            model = words(4)
        	    if line .eq. 6944 then
        	       a = model .eq. type
	            end if
        	    if model .eq. type then
                	      startDate = date
        	              return(startDate)
	            end if
        	end if
	        delete(words)
	   end do
;   end if
   return(startDate)
end

function getATCFTrack( fileName )
; ---- read in all the data points (in 3 or 6 hours apart) for the input ATCF track file ---------
begin

    track_data=new((/3,43/), float, default_fillvalue("float"))
;    if (fileexists(fileName)) then
  
	track = asciiread(fileName, -1,"string") 
	track_xp=new(43, float, default_fillvalue("float"))
	track_yp=new(43, float, default_fillvalue("float"))
	track_w=new(43, float, default_fillvalue("float"))
	track_hrs=new(43, integer, default_fillvalue("integer"))

        track = asciiread(fileName, -1,"string") 
	count=0
	do line = 0,dimsizes(track)-1
	  words=str_split(track(line),",")
	  w=stringtofloat(words(8))
	  hr = stringtointeger(words(5))
	  if (((hr%6 .eq. 0) .and. (count .eq. hr/6)) .or. ((hr%3  .eq. 0) .and.  (count .eq. hr/3))) then
	      index=hr/3
	      if isStrSubset(words(7),"W") then
        	  x=-stringtofloat(words(7))/10.0
	      else
	          x=stringtofloat(words(7))/10.0
	      end if

              if isStrSubset(words(6),"S") then
                  y=-stringtofloat(words(6))/10.0
              else
                  y=stringtofloat(words(6))/10.0
              end if
             
             if index .lt. 43 then
	         track_xp(index)=x
	         track_yp(index)=y
     	         track_w(index)=stringtofloat(words(8))
                 track_hrs(index)=hr
             end if

	     count=count+1
	  end if
	  delete(words)
	end do
        track_data(0,:)=track_xp
        track_data(1,:)=track_yp
        track_data(2,:)=track_w
;    end if
 
    return(track_data)
end

function getATCFTrack_2( fileName, stormID ) ; for hafs atcf file which may contain more than 
; ---- read in all the data points (in 3 or 6 hours apart) for the input ATCF track file ---------
begin
    tID = stringtochar(stormID)
     sID = chartostring(tID(0))+chartostring(tID(1))


    track_data=new((/3,maxLen/), float, default_fillvalue("float"))
;    if (fileexists(fileName)) then

        track = asciiread(fileName, -1,"string")
        track_xp=new(maxLen, float, default_fillvalue("float"))
        track_yp=new(maxLen, float, default_fillvalue("float"))
        track_w=new(maxLen, float, default_fillvalue("float"))
        track_hrs=new(maxLen, integer, default_fillvalue("integer"))

        track = asciiread(fileName, -1,"string")
        count=0
        do line = 0,dimsizes(track)-1
          words=str_split(track(line),",")
          AB = stringtochar(words(1))
          ID=chartostring(AB(1))+chartostring(AB(2))  ; chartostring(AB(0)+AB(1))

          if sID  .eq. ID then

          w=stringtofloat(words(8))
          hr = stringtointeger(words(5))
          if (((hr%6 .eq. 0) .and. (count .eq. hr/6)) .or. ((hr%3  .eq. 0) .and.  (count .eq. hr/3))) then
              index=hr/3
              if isStrSubset(words(7),"W") then
                  x=-stringtofloat(words(7))/10.0
              else
                  x=stringtofloat(words(7))/10.0
              end if

              if isStrSubset(words(6),"S") then
                  y=-stringtofloat(words(6))/10.0
              else
                  y=stringtofloat(words(6))/10.0
              end if

             if index .lt. maxLen then
                 track_xp(index)=x
                 track_yp(index)=y
                 track_w(index)=stringtofloat(words(8))
                 track_hrs(index)=hr
             end if

             count=count+1
          end if
          end if ; when storm ID match
          delete(words)
        end do
        track_data(0,:)=track_xp
        track_data(1,:)=track_yp
        track_data(2,:)=track_w
;    end if

    return(track_data)
end


function getATCFTrack_6Hr( fileName )
; ---- read in the data points (in 6 hour apart) for the input ATCF track file ---------
begin

     track_data=new((/3,43/), float, default_fillvalue("float"))
;     if (isfile(fileName)) then
        track = asciiread(fileName, -1,"string") ;"/scratch3/NCEPDEV/hwrf/save/Keqin.Wu/data/harvey09l.2017082412_hmon/harvey09l.2017082412.trak.hmon.atcfunix",-1,"string")
        track_xp=new(43, float, default_fillvalue("float"))
        track_yp=new(43, float, default_fillvalue("float"))
        track_w=new(43, float, default_fillvalue("float"))
        track_hrs=new(43, integer, default_fillvalue("integer"))
        count=0
        do line = 0,dimsizes(track)-1
          words=str_split(track(line),",")
          w=stringtofloat(words(8))
          hr = stringtointeger(words(5))
          if ((hr%6 .eq. 0) .and. (count .eq. hr/6)) then
              index=hr/6
              if isStrSubset(words(7),"W") then
                  x=-stringtofloat(words(7))/10.0
              else
                  x=stringtofloat(words(7))/10.0
              end if

              if isStrSubset(words(6),"S") then
                  y=-stringtofloat(words(6))/10.0
              else
                  y=stringtofloat(words(6))/10.0
              end if

              if index .lt. 43 then
                   track_xp(index)=x
                   track_yp(index)=y
                   track_w(index)=stringtofloat(words(8))
                   track_hrs(index)=hr
              end if

             count=count+1
          end if
          delete(words)
        end do
        track_data(0,:)=track_xp
        track_data(1,:)=track_yp
        track_data(2,:)=track_w
;    end if
    return(track_data)
end

function getATCFTrack_6Hr_2( fileName, stormID)  ; read a atcf file of one or more storms (hafs), stormID: string of the storm number
; ---- read in the data points (in 6 hour apart) for the input ATCF track file ---------
begin
     tID = stringtochar(stormID)
     sID = chartostring(tID(0))+chartostring(tID(1))

     track_data=new((/3,maxLen/), float, default_fillvalue("float"))
;     if (isfile(fileName)) then
        track = asciiread(fileName, -1,"string")
        track_xp=new(maxLen, float, default_fillvalue("float"))
        track_yp=new(maxLen, float, default_fillvalue("float"))
        track_w=new(maxLen, float, default_fillvalue("float"))
        track_hrs=new(maxLen, integer, default_fillvalue("integer"))
        count=0
        do line = 0,dimsizes(track)-1
          words=str_split(track(line),",")
          AB = stringtochar(words(1))
          ID=chartostring(AB(1))+chartostring(AB(2))  ; chartostring(AB(0)+AB(1))

          if sID  .eq. ID then
            print("----------------------")
          w=stringtofloat(words(8))
          hr = stringtointeger(words(5))
          if ((hr%6 .eq. 0) .and. (count .eq. hr/6)) then
              index=hr/6
              if isStrSubset(words(7),"W") then
                  x=-stringtofloat(words(7))/10.0
              else
                  x=stringtofloat(words(7))/10.0
              end if

              if isStrSubset(words(6),"S") then
                  y=-stringtofloat(words(6))/10.0
              else
                  y=stringtofloat(words(6))/10.0
              end if

              if index .lt. maxLen then
                   track_xp(index)=x
                   track_yp(index)=y
                   track_w(index)=stringtofloat(words(8))
                   track_hrs(index)=hr
              end if

             count=count+1
          end if
          end if ; if the stormID match
          delete(words)
        end do
        track_data(0,:)=track_xp
        track_data(1,:)=track_yp
        track_data(2,:)=track_w
;    end if
    return(track_data)
end


function getADeck( fileName, type, startDate )
begin
; ---- take value for every 6 hr-------
  xy=new((/3,43/),float, default_fillvalue("float"))

;  if (fileexists(fileName)) then
    data = asciiread(fileName,-1,"string")
    lineNumber = dimsizes(data)
    xp=new(43, float, default_fillvalue("float"))
    yp=new(43, float, default_fillvalue("float"))
    maxw=new(43, float, default_fillvalue("float"))

    ;hrs=new(43, integer, default_fillvalue("integer"))
    if strlen(type) .lt. 4 then
        type = " " + type
    end if
    if strlen(type) .lt. 5 then
        type = " " + type
    end if

    count=0
    hr1=-1
    do line = 0,lineNumber-1
        words=str_split(data(line),",")
        if (dimsizes(words) .gt. 7) then
            date = stringtointeger(words(2))
            if date .eq. startDate then
               model=words(4)
               hr0 = stringtointeger(words(5))
               if model .eq. type then
                   if (hr0 .ne. hr1) .and. (hr0 .le. 126) .and. (hr0%6 .eq. 0) then
                       index = hr0/3
                       if isStrSubset(words(7),"W") then
                           xp(count)=-stringtofloat(words(7))/10.0
                       else
                           xp(count)=stringtofloat(words(7))/10.0
                       end if

                       if isStrSubset(words(6),"S") then
                           yp(count)=-stringtofloat(words(6))/10.0
                       else
                           yp(count)=stringtofloat(words(6))/10.0
                       end if

                       maxw(count)=stringtofloat(words(8))

                       ;hrs(count)=hr0
                       count=count+1
                       hr1 = hr0
                   end if
               end if
           end if
       end if
       delete (words)
    end do

    xy(0,:)=xp(0:42:1)
    xy(1,:)=yp(0:42:1)
    xy(2,:)=maxw(0:42:1)

;  end if
  return(xy)
end

function getBDeck( fileName, startDate, length )
begin
; length: hours after startDate
; usually, give it value 126
; for composite plot, give it a bigger than possible number, e.g. 600

pnum = length/3 + 1
best = new((/3,pnum/), float, default_fillvalue("float"))

;if (fileexists(fileName)) then

	pnum = length/3 + 1
	best_xp=new(pnum, float, default_fillvalue("float"))
	best_yp=new(pnum, float, default_fillvalue("float"))
	best_w=new(pnum, float, default_fillvalue("float"))

	best_hrs=new(pnum, integer, default_fillvalue("integer"))

	best_track = asciiread(fileName,-1,"string")

	lineNumber = dimsizes(best_track)

	isConnected=0   ;check if the track does not belong to another invest with the same ID

	date1=0

	count=0

	startHour=getTimeHour(startDate)
	do line = 0,lineNumber-1
	  words=str_split(best_track(line),",")
	  if (dimsizes(words) .gt. 7) then
        	date = stringtointeger(words(2))
	        hour = getTimeHour(date)
        	if ((date .ge. startDate) .and. (date .ne. date1) .and. (hour-startHour .lt. length)) then
                	if (date .le. startDate) then
	                    isConnected=1
        	        end if
                	date1 = date

	                if isStrSubset(words(7),"W") then
        	            w=-stringtofloat(words(7))/10.0
                	else
	                    w=stringtofloat(words(7))/10.0
        	        end if

                	if isStrSubset(words(6),"S") then
	                    n=-stringtofloat(words(6))/10.0
        	        else
                	    n=stringtofloat(words(6))/10.0
	                end if


        	        maxw=stringtofloat(words(8))

                	best_xp(count)=w
	                best_yp(count)=n
        	        best_hrs(count)=doubletoint(hour-startHour)
                	best_w(count)=maxw
	                count=count+1
        	end if
	  end if
	  delete(words)
	end do
	isConnected=0   ;check if the track does not belong to another invest with the same ID
	date1=0
	count=0
	do line = 0,lineNumber-1
	  words=str_split(best_track(line),",")
	  if (dimsizes(words) .gt. 7) then
        	date = stringtointeger(words(2))
	        hour = getTimeHour(date)
        	if ((date .ge. startDate) .and. (date .ne. date1) .and. (hour-startHour .lt. length)) then
                	if (date .le. startDate) then
	                    isConnected=1
        	        end if

                	date1 = date
	                if isStrSubset(words(7),"W") then
        	            w=-stringtofloat(words(7))/10.0
                	else
	                    w=stringtofloat(words(7))/10.0
        	        end if

                	if isStrSubset(words(6),"S") then
	                    n=-stringtofloat(words(6))/10.0
        	        else
                	    n=stringtofloat(words(6))/10.0
	                end if

        	        maxw=stringtofloat(words(8))

                	best_xp(count)=w
	                best_yp(count)=n
        	        best_w(count)=maxw

                	count=count+1
	        end if
	  end if
	  delete(words)
	end do

	  best(0,:) = best_xp
	  best(1,:) = best_yp
	  best(2,:) = best_w
;end if
   return(best)

end

function getBDeck_2(fileName, startDate)
; get BDeck intensity for composite plot
begin

pnum=201
outputTracks = new((/3,pnum/), float, default_fillvalue("float"))

;if (fileexists(fileName)) then

best_track = asciiread(fileName,-1,"string")
lineNumber = dimsizes(best_track)

bp1=new(pnum, float, default_fillvalue("float"))
bp2=new(pnum, float, default_fillvalue("float"))
best_hrs=new(pnum, integer, default_fillvalue("integer"))

isConnected=0   ;check if the track does not belong to another invest with the same ID

date1=0
count=0
startHour=getTimeHour(startDate)

do line = 0,lineNumber-1
  words=str_split(best_track(line),",")
  if (dimsizes(words) .gt. 7) then
        date = stringtointeger(words(2))
        hour = getTimeHour(date)
        ;hdiff = hourDiff(startDate, date)
        if ((date .ge. startDate) .and. (date .ne. date1) .and. (date-startDate .lt. 17000)) then
        ;if ((date .ge. startDate) .and. (hdiff .le. 127) .and. (date .ne. date1) .and. (date-startDate .lt. 17000)) then

                if (date .le. startDate) then
                    isConnected=1
                end if
                date1 = date

                maxw=stringtofloat(words(8))
                minp=stringtofloat(words(9))
                best_hrs(count)=doubletoint(hour-startHour)
                bp1(count)=maxw
                bp2(count)=minp

                count=count+1
        end if
  end if
  delete(words)
end do

best_maxw=bp1
best_minp=bp2

outputTracks(0,:)=best_maxw(:)
outputTracks(1,:)=best_minp(:)
outputTracks(2,:)=best_hrs(:)

;end if

return(outputTracks)

end

function getBDeck_3(fileName, startDate)
; ---- get Best Track to composite tracks -----
begin

;---Read in best track

outputTracks = new((/3,80/), float, default_fillvalue("float"))

;if (fileexists(fileName)) then

best_xp = new(80, float, default_fillvalue("float"))
best_yp = new(80, float, default_fillvalue("float"))
best_w = new(80, float, default_fillvalue("float"))
best_hrs = new(80, integer, default_fillvalue("integer"))

best_track = asciiread(fileName,-1,"string")
lineNumber = dimsizes(best_track)

startHour=getTimeHour(startDate)
date1=0
count=0
do line = 0,lineNumber-1
  words=str_split(best_track(line),",")
  if (dimsizes(words) .gt. 7) then
        date = stringtointeger(words(2))
         hour = getTimeHour(date)
        if ((date .ge. startDate) .and. (date .ne. date1) .and. (date-startDate .lt. 17000)) then
                date1 = date
                if isStrSubset(words(7),"W") then
                    w=-stringtofloat(words(7))/10.0
                else
                    w=stringtofloat(words(7))/10.0
                end if

                if isStrSubset(words(6),"S") then
                    n=-stringtofloat(words(6))/10.0
                else
                    n=stringtofloat(words(6))/10.0
                end if


                maxw=stringtofloat(words(8))
                best_hrs(count)=doubletoint(hour-startHour)
                best_xp(count)=w
                best_yp(count)=n
                best_w(count)=maxw

                count=count+1
        end if
  end if
  delete(words)
end do

outputTracks(0,:)=best_xp
outputTracks(1,:)=best_yp
outputTracks(2,:)=best_w

;end if

return(outputTracks)
end



function getADeck_2( fileName, type, startDate )
;------ read ADeck for composite plot
begin
   pnum=201
;   if .not. (fileexists(fileName)) then
;      output = new((/1, 4,pnum/),float, default_fillvalue("float"))
;      return(output)
;   end if

   startYear = tointeger(startDate/10000.0)
   outputTracks = new((/pnum, 4, pnum/),float)
   data = asciiread(fileName,-1,"string")
   lineNumber = dimsizes(data)
   intensity=new((/4,pnum/),float, default_fillvalue("float"))
   hrs=new(pnum, float, default_fillvalue("float"))
   maxw=new(pnum, float, default_fillvalue("float"))
   minp=new(pnum, float, default_fillvalue("float"))

   dates=new(pnum, float)
   if strlen(type) .lt. 4 then
        type = " " + type
    end if
    if strlen(type) .lt. 5 then
        type = " " + type
    end if

    trackCount = 0
    read = False
    count = 0
    hr1 = -1
    ADate = -1
    do line = 0,lineNumber-1
        words = str_split(data(line),",")
        if (dimsizes(words) .gt. 7) then
           date = stringtointeger(words(2))
           model = words(4)
           hdiff = hourDiff(startDate, date)
           if (hdiff .lt. pnum*4+1) .and. (hdiff .ge. 0) then

            if (date .ge. startDate) .and. (date .ne. ADate) .and. (model .eq. type ) then
               count=0
               ADate = date
               read = True
            else if (date .eq. ADate) .and. (model .eq. type)  then
                   read = True
                 else
                   read = False
            end if
            end if
           else
             read = False
    end if
            if read then
               hr0 = stringtointeger(words(5))
               if model .eq. type then
                    if (hr0 .ne. hr1) .and. (hr0 .le. 126) then
                       index = hr0/3
                       maxw(count)=stringtofloat(words(8))
                       if stringtofloat(words(9)) .ne. 0 then
                            minp(count)=stringtofloat(words(9))
                       end if
                       dates(count) = tofloat(date-startYear*10000)
                       hrs(count)=hr0
                       count=count+1
                       hr1 = hr0
                   end if

               end if
           end if
       end if
       delete (words)
       if ( .not. read) .and. (count .gt. 0) .and. (trackCount .lt. pnum ) then

           intensity(0,:)=maxw
           intensity(1,:)=minp
           intensity(2,:)=hrs
           intensity(3,:)=dates
           outputTracks(trackCount,:,:)=intensity
           trackCount = trackCount + 1
           count = 0
       end if
    end do
    if (count .ne. 0) .and. (trackCount .lt. pnum) then
           intensity(0,:)=maxw
           intensity(1,:)=minp
           intensity(2,:)=hrs
           intensity(3,:)=dates
           outputTracks(trackCount,:,:)=intensity
           trackCount = trackCount + 1
    end if
    output = new((/trackCount, 4,pnum/),float)
    do i=0,trackCount-1
        output(i, :, :) = outputTracks(i,:,:)
    end do


   return(output)
end

function getADeck_3( fileName, type, startDate)
;----- for composite tracks ---------------
begin


;  if .not. (fileexists(fileName)) then
;      output = new((/1, 4,43/),float, default_fillvalue("float"))
;      return(output)
;   end if


    startYear = tointeger(startDate/10000.0)
    outputTracks = new((/200, 4,43/),float)
    data = asciiread(fileName,-1,"string")
    lineNumber = dimsizes(data)
    xy=new((/4,43/),float)
    xp=new(43, float, default_fillvalue("float"))
    yp=new(43, float, default_fillvalue("float"))
    maxw=new(43, float, default_fillvalue("float"))
    dates=new(43, float)
    if strlen(type) .lt. 4 then
        type = " " + type
    end if
    if strlen(type) .lt. 5 then
        type = " " + type
    end if

    trackCount=0
    read = False
    count = 0
    hr1 = -1
    ADate = -1
    do line = 0,lineNumber-1
        words=str_split(data(line),",")
        if (dimsizes(words) .gt. 7) then
            date = stringtointeger(words(2))
            model = words(4)
            hdiff=hourDiff(date, startDate)
            if (model .eq. type ) then    ;(hdiff .lt. 200*4+1) .and. (hdiff .ge. 0) then

            if (date .ge. startDate) .and. (date .ne. ADate) then     ;.and. (model .eq. type ) then
               count=0
               ADate = date
               read = True
            else if (date .eq. ADate) .and. (model .eq. type)  then
                   read = True
                 else
                   read = False
            end if
            end if
           else
             read = False

          end if
            if read then
               hr0 = stringtointeger(words(5))
               if model .eq. type then
                   if (hr0 .ne. hr1) .and. (hr0 .le. 126) .and. (hr0%3 .eq. 0) then
                       index = hr0/3
                       yp(count)=stringtofloat(words(6))/10.0
                       if isStrSubset(words(7),"W") then
                           xp(count)=-stringtofloat(words(7))/10.0
                       else
                           xp(count)=stringtofloat(words(7))/10.0
                       end if
                       if isStrSubset(words(6),"S") then
                             yp(count)=-stringtofloat(words(6))/10.0
                       else
                             yp(count)=stringtofloat(words(6))/10.0
                       end if

                       maxw(count) = stringtofloat(words(8))
                       dates(count) = tofloat(date-startYear*10000)
                       count = count+1
                       hr1 = hr0
                   end if
               end if
           end if
       end if
       delete (words)
       if ( .not. read) .and. (count .gt. 0) .and. (trackCount .lt. 200 ) then
           xy(0,:)=xp(0:42:1)
           xy(1,:)=yp(0:42:1)
           xy(2,:)=maxw(0:42:1)
           xy(3,:)=dates(0:42:1)
           outputTracks(trackCount,:,:)=xy
           trackCount = trackCount + 1
           count = 0
           xp=new(43, float, default_fillvalue("float"))
           yp=new(43, float, default_fillvalue("float"))
           maxw=new(43, float, default_fillvalue("float"))
           dates=new(43, float)

           ;print(tointeger(xy(3,0))+tointeger(startYear*10000))
       end if
    end do
    if (count .ne. 0) .and. (trackCount .lt. 200) then
        xy(0,:)=xp(0:42:1)
        xy(1,:)=yp(0:42:1)
        xy(2,:)=maxw(0:42:1)
        xy(3,:)=dates(0:42:1)
        outputTracks(trackCount,:,:)=xy
        trackCount= trackCount+1
    end if
    output = new((/trackCount, 4,43/),float)
    do i=0,trackCount-1
        output(i, :, :) = outputTracks(i,:,:)
    end do
    return(output)
end



function getADeck_Intensity( fileName, type, startDate )
; ------- take value at every 6 hours ------------
begin

  intensity=new((/3,43/),float, default_fillvalue("float"))

;  if (fileexists(fileName)) then

    data = asciiread(fileName,-1,"string")
    lineNumber = dimsizes(data)
    maxw=new(43, float, default_fillvalue("float"))
    minp=new(43, float, default_fillvalue("float"))
    hrs=new(43, integer, default_fillvalue("integer"))
    if strlen(type) .lt. 4 then
        type = " " + type
    end if
    if strlen(type) .lt. 5 then
        type = " " + type
    end if
    tc=0
    count=0
    hr1=-1
    do line = 0,lineNumber-1
        words=str_split(data(line),",")
        if (dimsizes(words) .gt. 7) then
            date = stringtointeger(words(2))
            if date .eq. startDate then
               model=words(4)
               hr0 = stringtointeger(words(5))
               if model .eq. type then
                   if (hr0 .ne. hr1) .and. (hr0 .le. 126) .and. (hr0%6 .eq. 0) then
                       index = hr0/3
                       maxw(count)=stringtofloat(words(8))

                       if stringtofloat(words(9)) .ne. 0 then
                            minp(count)=stringtofloat(words(9))
                       end if

                       hrs(count)=hr0
                       count=count+1
                       hr1 = hr0
                   end if
               end if
           end if
       end if
       delete (words)
    end do
    intensity(0,:)=maxw(0:42:1)
    intensity(1,:)=minp(0:42:1)
    intensity(2,:)=hrs(0:42:1)

;    end if

    return(intensity)
end

function getATCFTrack_Intensity( fileName )
; ---- read in all the data points (in 3 hour apart) for the input ATCF track file ---------
begin
;----- read in track data

  intensity=new((/3,43/),float, default_fillvalue("float"))

;  if (fileexists(fileName)) then


  track = asciiread(fileName,-1,"string")
  p1=new(43, float, default_fillvalue("float"))
  p2=new(43, float, default_fillvalue("float"))
  track_hrs=new(43, integer, default_fillvalue("integer"))
  count=0
  do line = 0,dimsizes(track)-1
    words=str_split(track(line),",")
    maxw=stringtofloat(words(8))
    minp=stringtofloat(words(9))
    hr = stringtointeger(words(5))
    if (((hr%3 .eq. 0) .and. (count .eq. hr/3)) .or. ((hr%6  .eq. 0) .and.  (count .eq. hr/6))) then
       index=hr/3
       if index .lt. 43 then

          p1(index)=maxw
          p2(index)=minp
          track_hrs(index)=hr
       end if
       count=count+1
    end if
    delete(words)
  end do
  intensity(0,:)=p1 ;(0:count-1:1)
  intensity(1,:)=p2 ;(0:count-1:1)
  intensity(2,:)=track_hrs ;(0:count-1:1)

;  end if
  return(intensity)
end

function getATCFTrack_Intensity_6Hr( fileName )
; ---- read in the data points (in 6 hour apart) for the input ATCF track file ---------
begin

  intensity=new((/3,43/),float, default_fillvalue("float"))

;  if (isfile(fileName)) then

  track = asciiread(fileName,-1,"string")
  p1=new(43, float, default_fillvalue("float"))
  p2=new(43, float, default_fillvalue("float"))
  track_hrs=new(43, integer, default_fillvalue("integer"))
  count=0
  do line = 0,dimsizes(track)-1
    words=str_split(track(line),",")
    maxw=stringtofloat(words(8))
    minp=stringtofloat(words(9))
    hr = stringtointeger(words(5))
    if ((hr%6  .eq. 0) .and.  (count .eq. hr/6)) then
       index=hr/6
       if index .lt. 43 then
          p1(index)=maxw
          p2(index)=minp
          track_hrs(index)=hr
       end if
       count=count+1
    end if
    delete(words)
  end do
  intensity(0,:)=p1 ;(0:count-1:1)
  intensity(1,:)=p2 ;(0:count-1:1)
  intensity(2,:)=track_hrs ;(0:count-1:1)
;  end if
  return(intensity)
end

function getATCFTrack_Intensity_6Hr_2(fileName, stormID)
; ---- read in the data points (in 6 hour apart) for the input ATCF track file ---------
begin
   tID = stringtochar(stormID)
   sID = chartostring(tID(0))+chartostring(tID(1))


  intensity=new((/3,maxLen/),float, default_fillvalue("float"))

;  if (isfile(fileName)) then

  track = asciiread(fileName,-1,"string")
  p1=new(maxLen, float, default_fillvalue("float"))
  p2=new(maxLen, float, default_fillvalue("float"))
  track_hrs=new(maxLen, integer, default_fillvalue("integer"))
  count=0
  do line = 0,dimsizes(track)-1
    words=str_split(track(line),",")
    AB = stringtochar(words(1))
    ID=chartostring(AB(1))+chartostring(AB(2))  ; chartostring(AB(0)+AB(1))

    if sID  .eq. ID then

      maxw=stringtofloat(words(8))
      minp=stringtofloat(words(9))
      hr = stringtointeger(words(5))
      if ((hr%6  .eq. 0) .and.  (count .eq. hr/6)) then
         index=hr/6
         if index .lt. maxLen then
            p1(index)=maxw
            p2(index)=minp
            track_hrs(index)=hr
         end if
         count=count+1
      end if
    end if
    delete(words)
  end do
  intensity(0,:)=p1 ;(0:count-1:1)
  intensity(1,:)=p2 ;(0:count-1:1)
  intensity(2,:)=track_hrs ;(0:count-1:1)
;  end if
  return(intensity)
end


function getBDeck_Intensity( fileName, startDate)
begin

  intensity=new((/3,43/),float, default_fillvalue("float"))

;  if (fileexists(fileName)) then

  best_track = asciiread(fileName,-1,"string")
  lineNumber = dimsizes(best_track)
  bp1=new(43, float, default_fillvalue("float"))
  bp2=new(43, float, default_fillvalue("float"))
  best_hrs=new(43, integer, default_fillvalue("integer"))
  isConnected=0   ;check if the track does not belong to another invest with the same ID
  date1=0
  count=0
  startHour=getTimeHour(startDate)
  do line = 0,lineNumber-1
    words=str_split(best_track(line),",")
    if (dimsizes(words) .gt. 7) then
        date = stringtointeger(words(2))
        hour = getTimeHour(date)
        if ((date .ge. startDate) .and. (date .ne. date1) .and. (hour-startHour .lt. 126)) then
                if (date .le. startDate) then
                    isConnected=1
                end if
                ;if (count .eq. 0 ) then
                ;     start_D = getStartD(words[7])
                ;end if
                date1 = date
                maxw=stringtofloat(words(8))
                minp=stringtofloat(words(9))
                best_hrs(count)=doubletoint(hour-startHour)
                bp1(count)=maxw
                bp2(count)=minp
                count=count+1
        end if
     end if
    delete(words)
  end do
  intensity(0,:)=bp1(0:42:1)
  intensity(1,:)=bp2(0:42:1)
  intensity(2,:)=best_hrs(0:42:1)
;  end if
  return(intensity)

end
