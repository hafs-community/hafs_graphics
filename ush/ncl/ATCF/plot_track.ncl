; ***********************************************
; Usage Examples:

;************************************************
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
loadscript("readTracks.ncl")
loadscript("colorPlans.ncl")
loadscript("addLegends.ncl")

begin

; stormName="irma"
; stormID="11l"
; startDate=2017090112

; atcfFile=""
; adeckFile="/scratch3/NCEPDEV/hwrf/save/Keqin.Wu/data/abdeck/aal092017.dat"
; bdeckFile="/scratch3/NCEPDEV/hwrf/save/Keqin.Wu/data/abdeck/bal092017.dat"

  if (.not. isvar("stormModel")) then
    stormModel="HWRF"
  end if

  if (.not. isvar("maxHour")) then
    maxHour=126
  end if
  track_pts=maxHour/3 + 1

  if (.not. isvar("catInfo")) then
    catInfo=True
  end if

  if (.not. isvar("fcstHour")) then
    fcstHour=False
  end if

  if (.not. isvar("figType")) then
    figType="png" ; x11, png, ps, pdf, ncgm, etc.
  end if

  if (.not. isvar("figName")) then
    figName=stormName + stormID  + "." + tostring(startDate) + ".track"
  end if

  wks=gsn_open_wks(figType, figName)

; Customized filled markers

  hrind=NhlNewMarker(wks, "p", 37, 0.0, 0.0, 1.0, 1.5, 0.0)   ;17 hurricane
  ciind=NhlNewMarker(wks, "Z", 37, 0.0, 0.0, 1.0, 0.8, 0.0)   ;18 circle
  sqind=NhlNewMarker(wks, "y", 35, 0.0, 0.0, 1.0, 1.0, 0.0)   ;19 square
  stind=NhlNewMarker(wks, "z", 35, 0.0, 0.0, 1.0, 1.8, 0.0)   ;20 star5
  s6ind=NhlNewMarker(wks, "l", 37, 0.0, 0.0, 1.0, 1.8, 0.0)   ;21 star6
  htind=NhlNewMarker(wks, "r", 35, 0.0, 0.0, 1.0, 1.5, 0.0)   ;22 heart
  diind=NhlNewMarker(wks, "q", 35, 0.0, 0.0, 1.0, 1.5, 0.0)   ;23 diamond
  clind=NhlNewMarker(wks, "p", 35, 0.0, 0.0, 1.0, 1.5, 0.0)   ;24 club
  spind=NhlNewMarker(wks, "s", 35, 0.0, 0.0, 1.0, 1.5, 0.0)   ;25 spade

  tuind=NhlNewMarker(wks, "u", 34, 0.0, 0.0, 1.0, 2.0, 0.0)   ;26 triangles
  trind=NhlNewMarker(wks, "u", 34, 0.0, 0.0, 1.0, 2.0, 90.0)  ;27
  tdind=NhlNewMarker(wks, "u", 34, 0.0, 0.0, 1.0, 2.0, 180.0) ;28
  tlind=NhlNewMarker(wks, "u", 34, 0.0, 0.0, 1.0, 2.0, 270.0) ;29

  tdind=NhlNewMarker(wks, "D",  1, 0.0, 0.0, 1.0, 1.0, 0.0)   ; TC categories
  tsind=NhlNewMarker(wks, "S",  1, 0.0, 0.0, 1.0, 1.0, 0.0)   ;
  h1ind=NhlNewMarker(wks, "1",  1, 0.0, 0.0, 1.0, 1.0, 0.0)   ;
  h2ind=NhlNewMarker(wks, "2",  1, 0.0, 0.0, 1.0, 1.0, 0.0)   ;
  h3ind=NhlNewMarker(wks, "3",  1, 0.0, 0.0, 1.0, 1.0, 0.0)   ;
  h4ind=NhlNewMarker(wks, "4",  1, 0.0, 0.0, 1.0, 1.0, 0.0)   ;
  h5ind=NhlNewMarker(wks, "5",  1, 0.0, 0.0, 1.0, 1.0, 0.0)   ;

; Candidate track colors (up to maximum 13 distinguishable colors)
; track color to choose from
;  modelColors=(/"purple", "black", "blue", "red", "green2", "cyan2", "orange1", "olivedrab1", "hotPink2", "dodgerblue",  "saddlebrown", "yellow2", "gray45"/)

  if (catInfo) then
    lineThickness=6.0
    markerSize=8.0
    markerThickness=3.0
  else
    lineThickness=4.0
    markerSize=6.0
    markerThickness=3.0
  end if

; modelLabels=(/"G217",     "G219",  "H218",   "F218",    "BEST" /)
; modelColors=(/"green2",   "blue",  "red",    "purple",  "black"/)
; modelMarkers=(/21,         23,      19,       18,        17/)
; modelMarkers=(/s6ind,      diind,   sqind,    ciind,     hrind  /)

  stormBasin=str_get_cols(stormID,2,2)

  if ( .not. isvar("modelLabels")) then

  if ( isStrSubset("LEClec",stormBasin) ) then
    modelLabels=(/"BEST",  "OFCL", stormModel, "HMON",   "CTCX",    "AVNO"/)
    modelColors=(/"black", "red",  "purple",   "green2", "orange1", "blue"/)
    modelMarkers=(/17,     18,     18,         18,       18,        18/)
;   modelLabels=(/"BEST",  "OFCL", stormModel, "HMON",   "CTCX",    "AVNO", "FV3G"/)
;   modelColors=(/"black", "red",  "purple",   "green2", "orange1", "blue", "saddlebrown"/)
;   modelMarkers=(/17,     18,     18,         18,       18,        18,     18/)
; ; modelMarkers=(/17,     22,     18,         19,       21,        23,     26/)
  else if ( isStrSubset("SPABspab",stormBasin) ) then
    modelLabels=(/"BEST",  "JTWC", stormModel, "CTCX",    "AVNO", "NVGM"/)
    modelColors=(/"black", "red",  "purple",   "orange1", "blue", "cyan2"/)
    modelMarkers=(/17,     18,     18,         18,        18,     18/)
;   modelLabels=(/"BEST",  "JTWC", stormModel, "COTC",    "AVNO", "FV3G",        "NVGM"/)
;   modelColors=(/"black", "red",  "purple",   "orange1", "blue", "saddlebrown", "cyan2"/)
;   modelMarkers=(/17,     18,     18,         18,        18,     18,            18/)
; ; modelMarkers=(/17,     22,     18,         21,        23,     26,            27/)
  else if ( isStrSubset("Ww",stormBasin) ) then
    modelLabels=(/"BEST",  "JTWC", stormModel, "CTCX",    "AVNO", "NVGM"/)
    modelColors=(/"black", "red",  "purple",   "orange1", "blue", "cyan2"/)
    modelMarkers=(/17,     18,     18,         18,        18,     18/)
;   modelLabels=(/"BEST",  "JTWC", stormModel, "COTC",    "TWRF",       "AVNO", "FV3G",        "NVGM"/)
;   modelColors=(/"black", "red",  "purple",   "orange1", "dodgerblue", "blue", "saddlebrown", "cyan2"/)
;   modelMarkers=(/17,     18,     18,         18,        18,           18,     18,            18/)
; ; modelMarkers=(/17,     22,     18,         21,        28,           23,     26,            27/)
  else
    print("Unknown basin")
    exit()
  end if
  end if
  end if

  end if

  trackNum=dimsizes(modelLabels)

  data1=new((/trackNum,track_pts/),float, default_fillvalue("float"))   ; clon
  data2=new((/trackNum,track_pts/),float, default_fillvalue("float"))   ; clat
  data3=new((/trackNum,track_pts/),float, default_fillvalue("float"))   ; Vmax
  ;;data4=new((/trackNum,track_pts/),float, default_fillvalue("float"))   ; Pmin
  data5=new((/trackNum,track_pts/),float, default_fillvalue("float"))   ; hour

  data1@_FillValue=default_fillvalue("float")
  data2@_FillValue=default_fillvalue("float")
  data3@_FillValue=default_fillvalue("float")
  ;;data4@_FillValue=default_fillvalue("float")
  data5@_FillValue=default_fillvalue("float")

  do i=0,trackNum-1
    if ( modelLabels(i) .eq. stormModel .and. fileexists(atcfFile) ) then
      print("Reading ATCF track")
      track_data=getATCFTrack_6Hr(atcfFile, maxHour)
      data1(i,:)=track_data(0,:)
      data2(i,:)=track_data(1,:)
      data3(i,:)=track_data(2,:)
      data5(i,:)=track_data(3,:)
    else if ( modelLabels(i) .eq. "BEST" .and. fileexists(bdeckFile) ) then
      print("Reading bdeck")
      best_data=getBDeck(bdeckFile, startDate, maxHour)
      data1(i,:)=best_data(0,:)
      data2(i,:)=best_data(1,:)
      data3(i,:)=best_data(2,:)
      data5(i,:)=best_data(3,:)
    else if ( fileexists(adeckFile) ) then
      print("Reading "+modelLabels(i)+" in adeck")
      xyw=getADeck(adeckFile, modelLabels(i), startDate, maxHour)
      data1(i,:)=xyw(0,:)
      data2(i,:)=xyw(1,:)
      data3(i,:)=xyw(2,:)
      data5(i,:)=xyw(3,:)
    end if
    end if
    end if
  end do

; Reset abnormal intensity values to default values
  data3=where(data3 .le. 0.001 .or. data3 .ge. 2000., data3@_FillValue, data3)

; Set some basic resources

  mpres=True
; Control appearance of map.
; mpres@mpProjection="CylindricalEquidistant
  mpres@mpGreatCircleLinesOn=True
  mpres@mpDataBaseVersion="MediumRes"    ; better map outlines
  mpres@mpDataSetName="Earth..2"
  mpres@mpOutlineBoundarySets="GeophysicalAndUSStates"

  mpres@mpGridAndLimbDrawOrder="PostDraw"
  mpres@mpGridAndLimbOn=True           ; turn on limb and grid lines
; mpres@mpGridLineColor=-1             ; ...but don't draw grid lines...
  mpres@mpGridLineColor="gray40"
  mpres@mpGridLineDashPattern=2
  mpres@mpGridLatSpacingF=5.0
  mpres@mpGridLonSpacingF=5.0
  mpres@mpPerimOn=True

  mpres@pmTickMarkDisplayMode  = "Always"           ; nicer tickmark labels

; mpres@mpFillOn=False          ; Default is False
  mpres@mpFillOn=True           ; Default is False
; mpres@mpFillDrawOrder="PreDraw"
; mpres@mpFillDrawOrder="PostDraw"     ; draw map fill last
  mpres@mpOutlineOn=True
  mpres@mpOutlineDrawOrder="PostDraw"
; mpres@mpOceanFillColor="lightskyblue1"
  mpres@mpLandFillColor="gray90"

; Zoom in on area
; mpres@mpLimitMode="LatLon"
; mpres@mpMinLatF=18.
; mpres@mpMaxLatF=65.
; mpres@mpMinLonF=-128.
; mpres@mpMaxLonF=-58.
; mpres@mpCenterLonF=-100.0
; mpres@mpCenterLatF=40.0

  res=mpres
  res@gsnDraw=False
  res@gsnFrame=False
; res@gsnMaximize=True           ; maximize plot in frame
; res@gsnPaperOrientation="portrait"
  res@cnFillOn=True           ; turn on contour fill
  res@cnFillMode="RasterFill"   ; faster
  res@cnRasterSmoothingOn=True           ;
; res@cnFillMode="CellFill"     ; faster
; res@cnLinesOn=False          ; turn off contour lines
; res@cnLineLabelsOn=False          ; turn off contour labels
; res@lbLabelBarOn=False          ; turn off labelbar

; res@cnInfoLabelOn=True
; res@cnInfoLabelFontHeightF=0.010
; res@cnInfoLabelPerimOn=False
;;res@cnInfoLabelString="Min: $ZMN$ Max: $ZMX$"
; res@cnInfoLabelString="Max: $ZMX$"

; res@tiMainString="NCEP HWRF"
; res@tiMainString="TC Tracks"
; res@gsnLeftString="Track"
  res@gsnLeftString=stormModel+" "+str_upper(stormName)+"("+str_upper(stormID)+")"
; res@gsnCenterString="Track"
; res@gsnRightString=str_upper(stormName) + "(" + str_upper(stormID) + ") " + tostring(startDate)
  res@gsnRightString="Init: "+tostring(startDate)

  res@gsnLeftStringOrthogonalPosF=0.05
  res@gsnCenterStringOrthogonalPosF=0.058
  res@gsnRightStringOrthogonalPosF=0.058

  if (catInfo)
    res@gsnLeftStringOrthogonalPosF=0.10
    res@gsnCenterStringOrthogonalPosF=0.108
    res@gsnRightStringOrthogonalPosF=0.108
  end if

  res@gsnStringFontHeightF=0.016
  res@gsnLeftStringFontHeightF=0.016
  res@gsnCenterStringFontHeightF=0.016
  res@gsnRightStringFontHeightF=0.016

  res@tiMainFontHeightF=0.018
  res@tiXAxisFontHeightF=0.016
  res@tiYAxisFontHeightF=0.016

  res@tmXBLabelFontHeightF=0.015
  res@tmXBMajorLengthF=0.016
  res@tmXBMinorLengthF=0.010
  res@tmYLLabelFontHeightF=0.015
  res@tmYLMajorLengthF=0.016
  res@tmYLMinorLengthF=0.010

  res@vpXF=0.2
  res@vpYF=0.8
  res@vpWidthF=0.6
  res@vpHeightF=0.6

  pres=True
; pres@gsLineThicknessF=3.0
  pres@gsLineColor="gray"

  mres=True
; mres@gsMarkerIndex=16
; mres@gsMarkerSizeF=8.0
; mres@gsMarkerColor="red"

  txres=True
  txres@txFontHeightF=0.01
; txres@txFont=22; helvetica bold

;************************************************
; create plot
;************************************************
; range
  latlonrange=0.60

  gsn_define_colormap(wks,"BlAqGrYeOrRevi200")

  maxLonF=max(data1)
  maxLatF=max(data2)
  minLonF=min(data1)
  minLatF=min(data2)
  disLatF=(maxLatF-minLatF)*latlonrange
  meanLatF=(minLatF + maxLatF)/2.0

  ; special case on Longitude
  if (maxLonF - minLonF) .gt. 180 then     ; Cross the dateline
    data1_1=where(data1.lt.0, 360+data1, data1)
    maxLonF=max(data1_1)
    minLonF=min(data1_1)
    print(maxLonF)
    print(minLonF)
    meanLonF=(minLonF + maxLonF) / 2.0
    if meanLonF .gt. 180 then
       meanLonF=meanLonF - 360
    end if
    disLonF=(maxLonF-minLonF)*latlonrange
  else
    meanLonF=(minLonF + maxLonF)/2.0
    disLonF=(maxLonF-minLonF)*latlonrange
  end if

  disLatF=max((/disLonF, disLatF, 10./))
  disLonF=max((/disLonF, disLatF, 10./))

; disLatF=max((/disLatF, 10./))
; disLonF=max((/disLonF, 10./))

  minLatF=max((/-90., meanLatF - disLatF/))
  maxLatF=min((/ 90., meanLatF + disLatF/))

  minLonF=meanLonF - disLonF
  maxLonF=meanLonF + disLonF

  res@mpMinLatF=floor(minLatF/5)*5.0
  res@mpMaxLatF=ceil(maxLatF/5)*5.0
  res@mpMinLonF=floor(minLonF/5)*5.0
  res@mpMaxLonF=ceil(maxLonF/5)*5.0
  res@mpCenterLonF=meanLonF
; res@mpCenterLatF=meanLatF ; setting mpCenterLatF may change map's projection mode

  if (disLatF .gt. 10. .or. disLonF .gt. 10.) then
    res@mpGridLatSpacingF=10.0
    res@mpGridLonSpacingF=10.0
  end if

  if (disLatF .gt. 30. .or. disLonF .gt. 30.) then
    res@mpGridLatSpacingF=20.0
    res@mpGridLonSpacingF=20.0
  end if

  markers=new(track_pts, graphic)
  lines=new(trackNum, graphic)
  circles= new(trackNum, graphic)
  points=new((/trackNum,track_pts/), graphic)
  lineSegs=new((/trackNum,track_pts/), graphic)
  markercats=new((/trackNum,track_pts/), graphic)
  texts=new((/trackNum,track_pts/), graphic)
  circlecats=new((/trackNum,track_pts/), graphic)
  circles_m=new(track_pts,graphic)
  circles_b=new(track_pts,graphic)

  plot=gsn_csm_map(wks,res)

  do m =0,trackNum-1
    i=trackNum-1-m
    print("Drawing "+modelLabels(i))
    pres@gsLineColor=modelColors(i)
    pres@gsLineThicknessF=lineThickness
    ; Draw track line
    if .not. ismissing(data1(i,0)) then
      if maxLonF .gt. 180 then
        data1(i,:)=where(data1(i,:).lt.0, 360+data1(i,:), data1(i,:))
      end if
      lineSegs(i,0)=gsn_add_polyline(wks, plot, data1(i,:), data2(i,:), pres)
    end if
    ; Draw track marker
    do k=0, track_pts-1
    ; mres@gsMarkerColor=getCategoryColor(data3(i,k))
      mres@gsMarkerColor=modelColors(i)
      mres@gsMarkerSizeF=markerSize
      mres@gsMarkerThicknessF=markerThickness
      mres@gsMarkerIndex=modelMarkers(i)
      points(i,k)=gsn_add_polymarker(wks,plot, data1(i,k), data2(i,k), mres)

      if (catInfo) then
      ; mres@gsMarkerColor=catColor(data3(i,k))
      ; mres@gsMarkerSizeF=markerSize*0.8
      ; mres@gsMarkerThicknessF=markerThickness
      ; mres@gsMarkerIndex=ciind
      ; circlecats(i,k)=gsn_add_polymarker(wks,plot, data1(i,k), data2(i,k), mres)

      ; mres@gsMarkerColor=modelColors(i)
      ; mres@gsMarkerColor=getCategoryColor(data3(i,k))
        mres@gsMarkerColor="white"
        mres@gsMarkerSizeF=markerSize*0.6
        mres@gsMarkerIndex=tdind
      ; mres@gsMarkerColor="skyblue2"
        if (.not. ismissing(data3(i,k))) then
          if (data3(i,k) .lt. 34.) then
            mres@gsMarkerIndex=tdind
          ; mres@gsMarkerColor="skyblue2"
          end if
          if (data3(i,k) .ge. 34.) then
            mres@gsMarkerIndex=tsind
          ; mres@gsMarkerColor="springgreen2"
          end if
          if (data3(i,k) .ge. 64.) then
            mres@gsMarkerIndex=h1ind
          ; mres@gsMarkerColor="darkorange2"
          end if
          if (data3(i,k) .ge. 83.) then
            mres@gsMarkerIndex=h2ind
          ; mres@gsMarkerColor="orangered2"
          end if
          if (data3(i,k) .ge. 96.) then
            mres@gsMarkerIndex=h3ind
          ; mres@gsMarkerColor="firebrick2"
          end if
          if (data3(i,k) .ge. 113.) then
            mres@gsMarkerIndex=h4ind
          ; mres@gsMarkerColor="deeppink2"
          end if
          if (data3(i,k) .ge. 137.) then
            mres@gsMarkerIndex=h5ind
          ; mres@gsMarkerColor="deeppink4"
          end if
        end if
        markercats(i,k)=gsn_add_polymarker(wks,plot, data1(i,k), data2(i,k), mres)
      end if

      if (fcstHour) then
        ; Add forecast hours for tracks
        txres@txFontColor=modelColors(i)
      ; txres@txJust="BottomLeft"
        txres@txJust="BottomCenter"
        hr=tointeger(data5(i,k))
        if (.not. ismissing(data3(i,k)) .and. hr%24 .eq. 0 .and. hr .ne. 0 ) then
        ; if (hr .lt. 10) then
        ;   dx=0.09
        ; else if (hr .lt. 100) then
        ;   dx=0.18
        ; else
        ;   dx=0.27
        ; end if
        ; end if
        ; texts(i,k) = gsn_add_text(wks,plot, tostring(hr), data1(i,k)+dx*(disLatF/50.0+1.1), data2(i,k)+1.5*(disLatF/50.0+0.2), txres)
          texts(i,k) = gsn_add_text(wks,plot, tostring(hr), data1(i,k), data2(i,k)+1.0*(disLatF/50.0), txres)
        end if
      end if

    end do
  end do

  bb=NhlGetBB((/plot/))
  left=0.2
  right=0.8
  itv=(right-left)/(trackNum)
  do i=0,trackNum-1
    px=left+i*itv
    py=bb(0)+0.012
    ;fontHeight=0.03+0.1*trackNum/13.0
    fontHeight=0.08
    placeAMarkerLineLegend(wks,modelLabels(i),px,py,itv*0.86,0.1,fontHeight,modelMarkers(i),modelColors(i),markerSize,lineThickness,4.0)
  end do

  if (catInfo) then
  ; Add legends for storm categories
  ; catLabels=(/"TD","TS","Cat-1","Cat-2","Cat-3","Cat-4","Cat-5"/)
    catLabels=(/"TD","TS","H1","H2","H3","H4","H5"/)
    catMarkers=(/tdind,tsind,h1ind,h2ind,h3ind,h4ind,h5ind/)
  ; catColors=(/getCategoryColor(17),getCategoryColor(34),getCategoryColor(64),getCategoryColor(83),getCategoryColor(96),getCategoryColor(113),getCategoryColor(137)/)
  ; catColors=(/catColor(17),catColor(34),catColor(64),catColor(83),catColor(96),catColor(113),catColor(137)/)
    catColors=(/"black", "black", "black", "black", "black", "black", "black"/)
    catNum=dimsizes(catLabels)
    left=0.3
    right=0.7
    itv=(right-left)/catNum
    do i=0,catNum-1
      px=left+i*itv
    ; py=bb(0)-0.005
    ; py=bb(0)-0.01
      py=bb(0)-0.015
    ; fontHeight=0.03+0.1*trackNum/13.0
      fontHeight=0.1
      placeAMarkerLegend(wks, catLabels(i), px, py, itv*0.86, 0.1, fontHeight, 18,            "black",      1.2*markerSize,     markerThickness)
      placeAMarkerLegend(wks, catLabels(i), px, py, itv*0.86, 0.1, fontHeight, catMarkers(i), "white",      1.2*0.6*markerSize, markerThickness)
    ; placeAMarkerLegend(wks, catLabels(i), px, py, itv*0.86, 0.1, fontHeight, catMarkers(i), catColors(i), 0.8*markerSize, markerThickness)
    end do
  end if

  draw(plot)
  frame(wks)

end

