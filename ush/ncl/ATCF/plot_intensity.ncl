;************************************************
;************************************************
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRFUserARW.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/contrib/cd_string.ncl"
loadscript("readTracks.ncl")
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

  if (.not. isvar("catInfo")) then
    catInfo=True
  end if

  if (.not. isvar("figType")) then
    figType="png" ; x11, png, ps, pdf, ncgm, etc.
  end if
  if (.not. isvar("figName")) then
    figName=stormName + stormID  + "." + tostring(startDate) + ".intensity"
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
; modelColors=(/"purple", "black", "blue", "red", "green2", "cyan2", "orange1", "olivedrab1", "hotPink2", "dodgerblue",  "saddlebrown", "yellow2", "gray45"/)

  lineThickness=5.0
  markerSize=0.008
  markerThickness=4.0

; modelLabels=(/"G217",     "G219",  "H218",   "F218",    "BEST" /)
; modelColors=(/"green2",   "blue",  "red",    "purple",  "black"/)
; modelMarkers=(/21,         23,      19,       18,        17/)
; modelMarkers=(/s6ind,      diind,   sqind,    ciind,     hrind  /)

; modelLabels=(/stormModel, "H218",   "G217",    "G219",  "BEST"/)
; modelColors=(/"purple",   "red",    "green2",  "blue",  "black"/)
; markerLineColor=(/"purple3",  "red3",   "green4",  "blue3", "black"/)

  stormBasin=str_get_cols(stormID,2,2)

  if ( .not. isvar("modelLabels")) then

  if ( isStrSubset("LEClec",stormBasin) ) then
     modelLabels=(/"BEST",  "OFCL", stormModel, "HMON",   "CTCX",    "AVNO", "SHF5"/)
     modelColors=(/"black", "red",  "purple",   "green2", "orange1", "blue", "skyblue"/)
     modelMarkers=(/17,     18,     18,         18,       18,        18,      18/)
;    modelLabels=(/"BEST",  "OFCL", stormModel, "HMON",   "CTCX",    "AVNO", "FV3G",        "SHF5"/)
;    modelColors=(/"black", "red",  "purple",   "green2", "orange1", "blue", "saddlebrown", "skyblue"/)
;    modelMarkers=(/17,     18,     18,         18,       18,        18,     18,             18/)
; ;  modelMarkers=(/17,     22,     18,         19,       21,        23,     26,             28/)
  else if ( isStrSubset("SPABspab",stormBasin) ) then
     modelLabels=(/"BEST",  "JTWC", stormModel, "CTCX",    "AVNO", "NVGM",  "SHF5"/)
     modelColors=(/"black", "red",  "purple",   "orange1", "blue", "cyan2", "skyblue"/)
     modelMarkers=(/17,     18,     18,         18,        18,     18,       18/)
;    modelLabels=(/"BEST",  "JTWC", stormModel, "COTC",    "AVNO", "FV3G",        "NVGM",  "SHF5"/)
;    modelColors=(/"black", "red",  "purple",   "orange1", "blue", "saddlebrown", "cyan2", "skyblue"/)
;    modelMarkers=(/17,     18,     18,         18,        18,     18,            18,       18/)
; ;  modelMarkers=(/17,     22,     18,         21,        23,     26,            27,       28/)
  else if ( isStrSubset("Ww",stormBasin) ) then
     modelLabels=(/"BEST",  "JTWC", stormModel, "CTCX",    "AVNO", "NVGM",  "SHF5"/)
     modelColors=(/"black", "red",  "purple",   "orange1", "blue", "cyan2", "skyblue"/)
     modelMarkers=(/17,     18,     18,         18,        18,     18,       18/)
;    modelLabels=(/"BEST",  "JTWC", stormModel, "COTC",    "TWRF",       "AVNO", "FV3G",        "NVGM",  "SHF5"/)
;    modelColors=(/"black", "red",  "purple",   "orange1", "dodgerblue", "blue", "saddlebrown", "cyan2", "skyblue"/)
;    modelMarkers=(/17,     18,     18,         18,        18,           18,     18,            18,       18/)
; ;  modelMarkers=(/17,     22,     18,         21,        28,           23,     26,            27,       28/)
  else
    print("Unknown basin")
    exit()
  end if
  end if
  end if

  end if

  trackNum=dimsizes(modelLabels)
  markerSizes=new(trackNum,float)
  markerThicknesses=new(trackNum,float)

  markerSizes(:)=markerSize
  markerThicknesses(:)=markerThickness

  data1=new((/trackNum,43/),float, default_fillvalue("float"))
  data2=new((/trackNum,43/),float, default_fillvalue("float"))
  data3=new((/trackNum,43/), integer, default_fillvalue("integer"))
  data1@_FillValue=default_fillvalue("float")
  data2@_FillValue=default_fillvalue("float")
  data3@_FillValue=default_fillvalue("integer")

  tempColors=modelColors
  tempMarkers=modelMarkers
  tempMarkerSizes=markerSizes
  tempMarkerThicknesses=markerThicknesses
  do m=0,trackNum-1
    i=trackNum-1-m
    tempColors(i)=modelColors(m)
    tempMarkers(i)=modelMarkers(m)
    tempMarkerSizes(i)=markerSizes(m)
    tempMarkerThicknesses(i)=markerThicknesses(m)
    if ( modelLabels(m) .eq. stormModel .and. fileexists(atcfFile) ) then
      atcfIntensity= getATCFTrack_Intensity_6Hr(atcfFile)
      data1(i,:)=atcfIntensity(0,:)
      data2(i,:)=atcfIntensity(1,:)
      data3(i,:)=toint(atcfIntensity(2,:))
    else if ( modelLabels(m) .eq. "BEST" .and. fileexists(bdeckFile) ) then
      best_track=getBDeck_Intensity(bdeckFile, startDate)
      data1(i,:)=best_track(0,:)
      data2(i,:)=best_track(1,:)
      data3(i,:)=toint(best_track(2,:))
    else if ( fileexists(adeckFile) ) then
      xyw=getADeck_Intensity(adeckFile, modelLabels(m), startDate )
      data1(i,:)=xyw(0,:)
      data2(i,:)=xyw(1,:)
      data3(i,:)=toint(xyw(2,:))
    end if
    end if
    end if
  end do

; Reset abnormal intensity values to default values
  data1=where(data1 .le. 0.001 .or. data1 .ge. 2000., data1@_FillValue, data1)
  data2=where(data2 .le. 0.001 .or. data2 .ge. 2000., data2@_FillValue, data2)

; print(max(data1))
; print(min(data1))
; print(min(data2))
; print(max(data2))

; Set plotting parameters
  res=True
  res@gsnMaximize=True
  res@gsnDraw=False
  res@gsnFrame=False

  res@xyMonoLineThickness=True
  res@xyMonoMarkerThickness=False

  res@vpXF=0.2
  res@vpYF=0.8

  res@vpWidthF=0.618 + 0.15
  res@vpHeightF=0.382

  res@trXMinF=0
  res@trXMaxF=126

; res@tmXBFormat="f"
; res@tmXBMode="Manual"
; res@tmXBTickStartF=0
; res@tmXBTickEndF=126
; res@tmXBTickSpacingF=12
; res@tmXBMinorPerMajor=3
; res@tmXBMinorPerMajor=1

  res@tmXBMode="Explicit"
  ymdh=tostring(startDate)
  fhourunits="hours since "+str_get_cols(ymdh,0,3)+"-"+str_get_cols(ymdh,4,5)+"-"+str_get_cols(ymdh,6,7)+" "+str_get_cols(ymdh,8,9)+":00"
  xticks=ispan(0,126,12)
  xticks@units=fhourunits
; cd_time=cd_calendar(xticks,-3)

; xlabels=tostring(xticks)
; timelabels=cd_string(xticks,"%D/%H")
; xlabels="   "+tostring(xticks)+"~C~"+timelabels
; xlabels(0)="    "+tostring(xticks(0))+"~C~"+timelabels(0)
; xlabels(9:10)=" "+tostring(xticks(9:10))+"~C~"+timelabels(9:10)

; xlabels=tostring(xticks)
; timelabels=cd_string(xticks,"%HZ%c%D")
; do i=0,dimsizes(xticks)-1,2
;   xlabels(i)="      "+tostring(xticks(i))+"~C~"+timelabels(i)
; end do 
; xlabels(0)="       "+tostring(xticks(0))+"~C~"+timelabels(0)
; xlabels(10)="     "+tostring(xticks(10))+"~C~"+timelabels(10)

  xlabels=tostring(xticks)
  timelabels=cd_string(xticks,"%N/%D/%HZ")
  do i=0,dimsizes(xticks)-1,2
    xlabels(i)="      "+tostring(xticks(i))+"~C~"+timelabels(i)
  end do 
  xlabels(0)="       "+tostring(xticks(0))+"~C~"+timelabels(0)
  xlabels(10)="     "+tostring(xticks(10))+"~C~"+timelabels(10)

; print(timelabels)
; print(xlabels)

  res@tmXBValues      = xticks
  res@tmXBLabels      = xlabels
  res@tmXBMinorValues=ispan(0,126,6)

  res@tmXTOn=False
  res@tmYROn=False

  yMin=max((/0., floor(min(data1)/10-1)*10./))
  yMax=ceil(max(data1)/10+1)*10.
  res@trYMinF=yMin
  res@trYMaxF=yMax

; res@tmYLFormat="f"
; res@tmYLMode="Manual"
; res@tmYLTickStartF=yMin
; res@tmYLTickEndF=yMax

  res@tmXMajorGrid=True
  res@tmXMajorGridLineDashPattern=2
  res@tmXMajorGridThicknessF=1.0
  res@tmXMajorGridLineColor="gray70"

  res@tmYMajorGrid=True
  res@tmYMajorGridLineDashPattern=2
  res@tmYMajorGridThicknessF=1.0
  res@tmYMajorGridLineColor="gray70"

  res@xyMonoMarkLineMode=True
  res@xyMarkLineMode="MarkLines"
  res@tiYAxisString="Max 10m Wind (kt)"
; res@tiXAxisString="Forecast Time (hr)"
  res@tiXAxisString="Forecast Hour and Valid Time"

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

  res@gsnLeftStringOrthogonalPosF=0.15
  res@gsnCenterStringOrthogonalPosF=0.158
  res@gsnRightStringOrthogonalPosF=0.158

  res@xyDashPattern=0
  res@xyMarkLineMode="MarkLines"
  res@xyMarkers=tempMarkers
  res@xyLineThicknessF=lineThickness
  res@xyLineColors=tempColors
  res@xyMarkerColors=res@xyLineColors
  res@xyMarkerThicknesses=tempMarkerThicknesses
  res@xyMarkerSizes=tempMarkerSizes

; res@gsnLeftString="Intensity Vmax"
; res@gsnRightString=str_upper(stormName) + "(" + str_upper(stormID) + ") " + tostring(startDate)

  res@gsnLeftString=stormModel+" "+str_upper(stormName)+"("+str_upper(stormID)+")"
; res@gsnCenterString="Vmax"
  res@gsnRightString="Init: "+tostring(startDate)

  if (catInfo) then
    res@tmYROn=True
    res@gsnYRefLine=(/34.,64.,83.,96.,113.,137./)
    res@gsnYRefLineThicknesses=(/1.0, 1.0, 1.0, 1.0, 1.0, 1.0/)
    res@gsnYRefLineColor="gray60"
    res@gsnYRefLineDashPattern=1

    res@tmYRMode="Explicit"
    res@tmYUseLeft=False
    res@tmYRLabelsOn=True
    res@tmYRMajorLengthF=0.0
    res@tmYRMinorLengthF=0.0
    res@tmYRLabelDeltaF=-1.4
  ; res@tmYRMajorThicknessF=3.0
    res@tmYRValues=(/34.,64.,83.,96.,113., 137./)
  ; res@tmYRLabels=(/"TS", "Cat-1", "Cat-2", "Cat-3", "Cat-4", "Cat-5"/)
    res@tmYRLabels=(/"TS", "H1", "H2", "H3", "H4", "H5"/)
  end if

  plot=gsn_csm_xy (wks,data3,data1,res)

  bb=NhlGetBB((/plot/))
  left=0.12
  right=0.88
  itv=(right-left)/(trackNum)
  do i=0,trackNum-1
    px=left+i*itv
  ; fontHeight=0.03+0.1*trackNum/13.0
    fontHeight=0.08
    placeAMarkerLineLegend(wks, modelLabels(i), px, bb(0), itv*0.86, 0.1, fontHeight, modelMarkers(i), modelColors(i), markerSizes(i), lineThickness, markerThicknesses(i))
  end do

  draw(plot)
  frame(wks)

; Plotting intensity Pmin

  yMin=max((/0., floor(min(data2)/10-1)*10./))
  yMax=ceil(max(data2)/10+1)*10.
  res@trYMinF=yMin
  res@trYMaxF=yMax

; res@gsnLeftString="Intensity Pmin"
; res@gsnRightString=str_upper(stormName) + "(" + str_upper(stormID) + ") " + tostring(startDate)

  res@gsnLeftString=stormModel+" "+str_upper(stormName)+"("+str_upper(stormID)+")"
; res@gsnCenterString="Pmin"
  res@gsnRightString="Init: "+tostring(startDate)

  res@tiYAxisString="Min Central Pressure (hPa)"

  if (catInfo) then
    delete(res@gsnYRefLine)
    res@gsnYRefLine=(/920., 945., 965., 980./)
    delete(res@gsnYRefLineThicknesses)
    res@gsnYRefLineThicknesses=(/1.0, 1.0, 1.0, 1.0/)
    res@gsnYRefLineColor="gray60"
    res@gsnYRefLineDashPattern=1

    res@tmYRMode="Explicit"
    res@tmYUseLeft=False
    res@tmYRLabelsOn=True
    res@tmYRMajorLengthF=0.0
    res@tmYRMinorLengthF=0.0
    res@tmYRLabelDeltaF=-1.4
  ; res@tmYRMajorThicknessF=3.0 ;
    delete(res@tmYRValues)
    res@tmYRValues=(/920., 945., 965., 980./)
    delete(res@tmYRLabels)
  ; res@tmYRLabels=(/"Cat-5", "Cat-4", "Cat-3", "Cat-2"/)
    res@tmYRLabels=(/"H5", "H4", "H3", "H2"/)
  end if

  plot=gsn_csm_xy (wks,data3,data2,res)

  bb=NhlGetBB((/plot/))
  left=0.12
  right=0.88
  itv=(right-left)/(trackNum)
  do i=0,trackNum-1
    px=left+i*itv
  ; fontHeight=0.03+0.1*trackNum/13.0
    fontHeight=0.08
    placeAMarkerLineLegend(wks, modelLabels(i), px, bb(0), itv*0.86, 0.1, fontHeight, modelMarkers(i), modelColors(i), markerSizes(i), lineThickness, markerThicknesses(i))
  end do

 draw(plot)
 frame(wks)

end
