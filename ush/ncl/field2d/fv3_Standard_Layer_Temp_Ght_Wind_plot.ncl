;----------------------------------------------------------------------

; ncl isStormDomain=False replace=False is6Hr=True 'graphicDir="/your/figure/dir"' 'stormModel="HAFS"' startDate=2019071506 startTimeLevel=0 endTimeLevel=11 'atcfFile="/hafs/com/2019071506/00L/natl00l.2019071506.trak.hafs.atcfunix.all"' 'stormDir="/hafs/com/2019071506/00L"' thisnclscript.ncl

; Orion example: ncl isStormDomain=False replace=True is6Hr=True 'graphicDir="/work/noaa/hwrf/save/kwu/HAFS2020Figures"' 'stormModel="HAFS"' standardLayer=500 startDate=2020070412 startTimeLevel=0 endTimeLevel=11 'atcfFile="/work/noaa/hwrf/save/kwu/HAFSGraphics/EMC_HAFSJ_2020rt/natl00l.2020070412/natl00l.2020070412.trak.hafs.atcfunix.all"'  'stormDir="/work/noaa/hwrf/save/kwu/HAFSGraphics/EMC_HAFSJ_2020rt/natl00l.2020070412/"' fv3_Standard_Layer_Temp_Ght_Wind_plot.ncl

; isStormDomain: plot for storm domain or whole domain
; is6Hur: make plots for every 6 forecast hour or 3 forefast hour
; replace: replace if an image is already there

;************************************************

; plot every 3 or 6 Hour
if (.not. isvar("is6Hr")) then
  is6Hr=True
end if

if ( is6Hr ) then
  maxLen = 22  ;
else
  maxLen = 43  ; number of forecasts. 43 for 126 hrs, 59 for 174 hr
end if

;-------------------------------------------------------------------
loadscript("readTracks.ncl")
loadscript("validTime.ncl")
loadscript("colorPlans.ncl")
;------------------------------------------------------------------

begin
if (.not. isvar("isStormDomain")) then
   isStormDomain=False
end if

if (.not. isvar("replace")) then
   replace=True  ; replace if the image is already there
end if

if (.not. isvar("graphicDir")) then
   graphicDir="/your/figure/dir"  ; replace if the image is already there
end if

if ( .not. isvar("standardLayer")) then
  standardLayer=850
end if

if ( .not. isvar("startTimeLevel")) then
  startTimeLevel=0
end if

if ( .not. isvar("endTimeLevel")) then
  endTimeLevel=maxLen-1
end if

print("===" + tostring(standardLayer) + "mb_Temp_Ght_Wind_plot===")

if (.not. isvar("stormModel")) then
    stormModel="HAFS"
end if

if (.not. isvar("figType")) then
   figType="png" ; x11, png, ps, pdf, ncgm, etc.
end if

if (.not. isvar("stormID")) .or. (.not. isvar("stormName")) then  ;;  if no stormID is given, draw all the storms from the track file
   sids=systemfunc("sh getStormIDs.sh "+atcfFile )
   names=systemfunc("sh getStormNames.sh "+atcfFile + " " + tostring(startDate))
   if strlen(sids) .gt. 0 then
      stormIDs=str_split(sids," ")
      stormNames=str_split(names," ")
      stormCount=dimsizes(stormIDs)
   else
      stormCount=0
   end if
   stormID="00l"
   stormName="natl"
else
   stormCount=1
   stormIDs=(/stormID/)
   stormNames=(/stormName/)
end if

if isstring(startDate) then
    sDate=tointeger(startDate)
    delete(startDate)
    startDate=sDate
end if

modelName = str_upper(stormModel)
stormID = str_upper(stormID)
stormName = str_upper(stormName)

sdstr = str_lower(stormName) + str_lower(stormID) + "." + tostring(startDate)
domain1_dir = stormDir + "/" + sdstr  + ".hafsprs.synoptic.0p03.f"   ;006.grb2  ;   sdstr + "." + str_lower(stormModel) +  "prs.synoptic.0p03.f"

;---------------- get tracks ---------------------------
if stormCount .gt. 0 then
   track_xp=new((/stormCount, maxLen/), float, default_fillvalue("float"))
   track_yp=new((/stormCount, maxLen/), float, default_fillvalue("float"))
   track_w=new((/stormCount, maxLen/), float, default_fillvalue("float"))
   line1 = new(stormCount, graphic)
   markers1 = new(stormCount, graphic)
   line2 = new(stormCount, graphic)
   markers1_2 = new(stormCount, graphic)

   markers2 = new(stormCount, graphic)
   ;markers2_2 = new(stormCount, graphic)
   ;markers2_3 = new(stormCount, graphic)
   markers3 = new(stormCount, graphic)
   texts_w1 = new(stormCount, graphic)
   texts_w2 = new(stormCount, graphic)
   texts_w3 = new(stormCount, graphic)
   texts_w4 = new(stormCount, graphic)
   texts = new(stormCount, graphic)
end if

do i = 0, stormCount-1
if ( is6Hr ) then
  track_data = getATCFTrack_6Hr_2(atcfFile,stormIDs(i))
else
  track_data = getATCFTrack_2(atcfFile,stormIDs(i))
end if
  track_xp(i,:)=track_data(0,:)
  track_yp(i,:)=track_data(1,:)
  track_w(i,:)=track_data(2,:)
end do

;-----------------------get domain boundary ----------------------------------

name0 = domain1_dir  +  "000.grb2"
grb_file_new=addfile(name0, "r")

lat=grb_file_new->lat_0
lon=grb_file_new->lon_0

lids=get1Dindex(grb_file_new->lv_ISBL0, standardLayer*100)
if ismissing(lids) then
   layerId = dimsizes(grb_file_new->lv_ISBL0)-1
else
   layerId = lids(0)
end if

minLat  =  min(lat)       ;12    ; min(lat) ; 7
maxLat  =  max(lat)       ;48    ; max(lat)  ; 47
minLon  =  min(lon)      ; -95
maxLon  =  max(lon)        ;-50   ; max(lon)  ; -55

;************************************************
; create plot
;************************************************

;;;-------res1---------
   res1                      = True               ; plot mods desired
   res1@cnFillOn             = True               ; turn on color for contours
   res1@cnLinesOn            = False              ; turn off contour lines
   res1@cnLineLabelsOn       = False              ; turn off contour line labels
   res1@cnLineColor = "white"
   
   res1@cnFillPalette = getColorMap("temperature")
   res1@cnFillOpacityF = 0.8
   res1@cnSpanFillPalette = True
   res1@cnFillMode = "RasterFill"
   res1@gsnMaximize           = True         ; enlarge plo

   res1@cnConstFEnableFill = True
   res1@cnConstFLabelOn    =  False          ; Turn off the "constant field" label in the middle of the plot
   res1@gsnAddCyclic = False

   res1@lbOrientation            = "Vertical"     ; vertical label bar
   res1@cnLevelSelectionMode = "ExplicitLevels" ;"ManualLevels"  ;"ExplicitLevels"
   res1@cnLevels =ispan(1,30,1)  ; ispan(2,30,2) 

   res1@pmLabelBarWidthF = 0.05
   res1@lbAutoManage=False
   res1@lbLabelStride=1
   res1@lbLabelFontHeightF = 0.0082

   res1@gsnDraw          = False                    ; turn off draw and frame
   res1@gsnFrame         = False                    ; b/c this is an overlay plot
   res1@cnFillDrawOrder   = "Draw"  ; draw contours first
   res1@mpOutlineDrawOrder = "Postdraw"
   res1@vpWidthF         = 0.7
   res1@vpHeightF         = 0.7
   res1@vpXF = 0.15
   res1@vpYF = 0.85
   res1@cnInfoLabelOn = False

   if isStormDomain then
      res1@mpGridLatSpacingF = 1.0
      res1@mpGridLonSpacingF = 1.0
      res1@tmXBTickSpacingF = 1.0
      res1@tmYLTickSpacingF = 1.0
      res1@gsnMinorLatSpacing = 1.0
      res1@gsnMinorLonSpacing = 1.0
      res1@pmLabelBarOrthogonalPosF = -0.012
      res1@pmLabelBarHeightF  = 0.705
   else
      res1@mpGridLatSpacingF = 5.0
      res1@mpGridLonSpacingF = 5.0
      res1@tmXBTickSpacingF = 10.0
      res1@tmYLTickSpacingF = 10.0
      res1@gsnMinorLatSpacing = 5.0
      res1@gsnMinorLonSpacing = 5.0
      res1@pmLabelBarOrthogonalPosF = -0.013 ; move laber bar further away
      res1@pmLabelBarHeightF  = 0.71*(maxLat-minLat)/(maxLon-minLon) ;0.515 for HAFC
  end if


   res1@mpDataBaseVersion      = "MediumRes"    ; better map outlines
   res1@mpDataSetName          = "Earth..2"
   res1@mpOutlineBoundarySets  = "GeophysicalAndUSStates"
   res1@mpGeophysicalLineThicknessF = 1.5	
   res1@mpUSStateLineThicknessF = 1.5
   res1@mpFillOn = False

   res1@mpGridAndLimbOn = True
   res1@mpGridLineColor = "gray40"
   res1@mpGridLineDashPattern = 2 

   res1@tmXBMinorOn = True
   res1@tmYLMinorOn = True

   res1@tmXBMinorPerMajor = 2
   res1@tmYLMinorPerMajor = 2
   res1@tmXBLabelFontHeightF = 0.01
   res1@tmYLLabelFontHeightF = 0.01

   res1@gsnLeftString = stormModel   + " " + stormName  + stormID ; "Operational " + stormModel
   res1@gsnStringFontHeightF = 0.012
   res1@tmXTOn = False
   res1@tmYROn = False
   res1@tiMainString =  tostring(standardLayer) +  "hPa Temp (~S~0~N~C), Geo. Height (x10m), and Wind (kt)" 

   res1@gsnLeftStringOrthogonalPosF = 0.006
   res1@gsnRightStringOrthogonalPosF = 0.006

   res1@tiMainFont = 21
   res1@tiMainFontHeightF = 0.013
   res1@tmXBMajorLengthF=0.008
   res1@tmXBMinorLengthF=0.004
   res1@tmYLMajorLengthF=0.008
   res1@tmYLMinorLengthF=0.004
  
   res1@mpMinLatF   = minLat  ;12    ; min(lat) ; 7
   res1@mpMaxLatF   = maxLat  ;48    ; max(lat)  ; 47
   res1@mpMinLonF   = minLon  ;-86   ; min(lon)   ; -95
   res1@mpMaxLonF   = maxLon  ;-50   ; max(lon)  ; -55

   res1@sfXArray         = lon(:)
   res1@sfYArray         = lat(:)

;;; ------------- res2 ------------ ;;;
   res2 = True
   ;res2@cnLevelSelectionMode = "ExplicitLevels" ;"ManualLevels"  ;"ExplicitLevels"
   ;res2@cnLevels            =   ispan(980,1030,2)  ;ispan(100,200,2) ;(/5, 7.5, 10, 12.5, 15, 17.5, 20, 25, 30, 40, 45, 50/)
   res2@cnLevelSelectionMode = "ExplicitLevels" ;"ManualLevels"  ;"ExplicitLevels"
   res2@cnLevels            =  ispan(100,200,2) ;(/5, 7.5, 10, 12.5, 15, 17.5, 20, 25, 30, 40, 45, 50/)
   res2@cnSmoothingOn = True
   res2@cnSmoothingDistanceF = 0.008

   ;res2@cnFillOn             = False               ; turn on color for contours
   res2@cnLinesOn            = True              ; turn off contour lines
   res2@cnLineLabelsOn       = True              ; turn off contour line labels
   ;res2@cnLineLabelPlacementMode = "Randomized"  ; "constant" often not work, computed
   ;res2@cnLineLabelInterval = 1
   res2@cnLineLabelDensityF = 5 ; does not work if cnLineLabelPlacementMode = "constant"
  
   res2@cnLineLabelFontHeightF = 0.007
   res2@cnLineLabelBackgroundColor = "transparent"
   res2@cnLabelMasking             = True
   ;res2@cnMonoLineColor = False

   res2@cnLineColor = "black"
   res2@cnLineThicknessF = 2 
   res2@gsnDraw          = False                    ; turn off draw and frame
   res2@gsnFrame         = False 
   res2@cnInfoLabelOn = False
   res2@gsnLeftString = ""
   res2@gsnRightString = ""
  
   res2@sfXArray         = lon(:)
   res2@sfYArray         = lat(:)

;;;------------- vres-----------;;;

   vres = True
   vres@vcRefMagnitudeF           = 10.0             ; define vector ref mag
   vres@vcRefLengthF              = 0.016 ;0.018          ; define length of vec ref
   vres@vcRefAnnoOn   = False         ; change ref vector color
   vres@vcMinDistanceF          = 0.018  ;17 ;0.0225 ;0.01 ;0.015
   
   ;vres@vcLineArrowColor        = "white"  ;  "white"  ;"blue"   ;"deeppink1"           ; change vector color
   ;vres@vcWindBarbColor   = "gray20" ; "royalblue1"
   vres@vcWindBarbLineThicknessF   = 1.3               ; change vector thickness
   vres@gsnAddCyclic = False
   vres@gsnDraw          = False                    ; turn off draw and frame
   vres@gsnFrame         = False                    ; b/c this is an overlay plot
   vres@vcGlyphStyle     = "WindBarb"         ; select wind barbs
   vres@vcMonoWindBarbColor     = False 
   vres@vcLevelSelectionMode    = "ExplicitLevels" ; will explicitly set the levels
   ;vres@vcLevels                = ispan(2,30,2)    ; set the levels 
   ;vres@vcLevelColors           = (/20,30,40,45,50,55,60,65,70,75,80,85,90,95/)   ; set the colors associated with the wind speed
   ;vres@vcLevelPalette  = (/"gray80","gray60","gray55","gray48","gray40","gray28","gray18","gray10","gray10","gray18","gray28","gray40","gray50","gray60","gray60", "gray80"/)
   vres@vcLevels                = ispan(1,30,1)
   vres@vcLevelPalette  = (/"gray80", "gray75", "gray70",  "gray47", "gray25", "gray20", "gray15", "gray15", "gray15", "gray15", "gray15", "gray15", "gray15", "gray15", "gray15", "gray15", "gray15", "gray15", "gray15", "gray15", "gray15", "gray15", "gray15", "gray15", "gray15",  "gray20", "gray25",   "gray47", "gray70", "gray75", "gray80"/)

   vres@lbLabelBarOn = False

   vres@vcVectorDrawOrder = "Postdraw"
   ;vres@vcPositionMode = "ArrowHead"

   vres@gsnLeftString = ""
   vres@gsnRightString = ""

   vres@vfXArray         = lon(:)
   vres@vfYArray         = lat(:)

;;;-------------pres------------;;;
   pres                  = True               ; polyline resources
   pres@gsLineColor      = "black"
   if isStormDomain then
      pres@gsLineThicknessF = 6.0                ; line thickness
   else
     pres@gsLineThicknessF = 3.75
   end if

   mres                = True         ; marker resources for best track
   ;mres@gsMarkerIndex  = 16           ; marker style (filled circle)
   mres@gsMarkerSizeF  = 6.0          ; marker size
   mres@gsMarkerColor  = "black"      ; maker color

   txres               = True
   txres@txFontHeightF = 0.012             ; Set the font height
   txres@txJust = "TopLeft"
   txres@txFont = 22 ; helvetica bold
 
format = "%Y%N%D%H"    ; "%Y (%HH)", "%d %c

if startTimeLevel .lt. 0 then
  startTimeLevel = 0
end if
if endTimeLevel .gt. maxLen-1 then
  endTimeLevel=maxLen-1
end if

do ifil = startTimeLevel, endTimeLevel
   if ( is6Hr ) then
      hour = sprinti("%0.3i",ifil*6)
   else  ; 3hr
      hour = sprinti("%0.3i",ifil*3)
   end if

   if (.not. isStormDomain) then
       figName =  graphicDir + "/" + stormName + stormID + "." + tostring(startDate) + "." +  modelName + "." + tostring(standardLayer) + "mb.temp.ght.wind.f" + hour
       if replace .or. ( .not. (fileexists( figName + "." + figType )) ) then
           print(ifil)
           wks = gsn_open_wks(figType,  figName)
           figName = figName +  "." + figType

           hrind = NhlNewMarker(wks, "p", 37, 0.0, 0.0, 1.0, 1.0, 0.0)
           name0 = domain1_dir  +  hour + ".grb2"

           ;res1@gsnRightString = stormName + "(" + stormID + ") " + tostring(startDate) + " F " + hour
           valid = validtime(startDate, tointeger(hour), format)
           res1@gsnRightString = "Init: " + tostring(startDate) + "Z, F" + hour  + ", Valid: " + valid + "Z"

           grb_file_new=addfile(name0, "r")

           u = grb_file_new->UGRD_P0_L100_GLL0(layerId,:,:)*1.94384  ; UGRD_P0_L100_GLL0
           v = grb_file_new->VGRD_P0_L100_GLL0(layerId,:,:)*1.94384  ; VGRD_P0_L100_GLL0
           T = grb_file_new->TMP_P0_L100_GLL0(layerId,:,:)-273.15
           H = grb_file_new->HGT_P0_L100_GLL0(layerId,:,:)/10.0

           plotV = gsn_csm_vector_scalar(wks, u, v, T, vres)
           plot = gsn_csm_contour_map(wks, T, res1)
           plot2 = gsn_csm_contour(wks, H, res2)

           overlay(plot,plot2)
           overlay(plot,plotV)

           do i = 0, stormCount-1

               mres@gsMarkerSizeF = 5.0
               mres@gsMarkerIndex = 16
               mres@gsMarkerThicknessF = 1.0

               mres@gsMarkerColor = "white"
               pres@gsLineColor = "white"
               line2(i) = gsn_add_polyline(wks,plot, track_xp(i,:)+0.1, track_yp(i,:)-0.1,pres)      ; draw the traj
               markers1_2(i) = gsn_add_polymarker(wks,plot,track_xp(i,:)+0.1,track_yp(i,:)-0.1,mres)

               mres@gsMarkerColor = "Black"
               pres@gsLineColor = "black"
               line1(i) = gsn_add_polyline(wks,plot,track_xp(i,:),track_yp(i,:),pres)      ; draw the traj
               markers1(i) = gsn_add_polymarker(wks,plot,track_xp(i,:),track_yp(i,:),mres)

               mres@gsMarkerSizeF = 12.0          ; marker size
               mres@gsMarkerIndex = hrind
               mres@gsMarkerThicknessF = 5.0

               mres@gsMarkerColor = "black"
               markers2(i) = gsn_add_polymarker(wks,plot,track_xp(i,ifil),track_yp(i,ifil),mres)

               mres@gsMarkerSizeF = 11.0          ; marker size
               mres@gsMarkerColor = "red2"  ;"black" ;deeppink3"
               mres@gsMarkerThicknessF = 2.0
               markers3(i) = gsn_add_polymarker(wks,plot,track_xp(i,ifil),track_yp(i,ifil),mres)

               txres@txFontColor = "black"
               texts(i) = gsn_add_text(wks,plot,stormNames(i), track_xp(i,0)+0.68, track_yp(i,0)-0.68, txres)
               txres@txFontColor = "white"
               texts_w1(i) = gsn_add_text(wks,plot,stormNames(i), track_xp(i,0)+0.82, track_yp(i,0)-0.82, txres)
               texts_w2(i) = gsn_add_text(wks,plot,stormNames(i), track_xp(i,0)+0.54, track_yp(i,0)-0.54, txres)
               texts_w3(i) = gsn_add_text(wks,plot,stormNames(i), track_xp(i,0)+0.82, track_yp(i,0)-0.54, txres)
               texts_w4(i) = gsn_add_text(wks,plot,stormNames(i), track_xp(i,0)+0.54, track_yp(i,0)-0.82, txres)
           end do

           draw(plot)
           frame(wks)
           system("convert -crop 985x630+18+194 " + figName + " " + figName)
        end if
    else
       ; --------- for storm domain ---------------
       do i = 0, stormCount-1
          figName =  graphicDir + "/" +stormNames(i) + "." + tostring(startDate) + "." +  modelName + ".storm." + tostring(standardLayer) + "mb.temp.ght.wind.f" + hour
          if .not. ismissing(track_xp(i,ifil)) .and. ( replace .or. ( .not. (fileexists( figName + "." + figType ) ) ) ) then
             print(ifil)
             wks = gsn_open_wks(figType,  figName)
             figName = figName +  "." + figType

             hrind = NhlNewMarker(wks, "p", 37, 0.0, 0.0, 1.0, 1.0, 0.0)
             name0 = domain1_dir  +  hour + ".grb2"
             valid = validtime(startDate, tointeger(hour), format)
             res1@gsnRightString = "Init: " + tostring(startDate) + "Z, F" + hour  + ", Valid: " + valid + "Z"

             grb_file_new=addfile(name0, "r")

             u = grb_file_new->UGRD_P0_L100_GLL0(layerId,:,:)*1.94384  ; UGRD_P0_L100_GLL0
             v = grb_file_new->VGRD_P0_L100_GLL0(layerId,:,:)*1.94384  ; VGRD_P0_L100_GLL0
             T = grb_file_new->TMP_P0_L100_GLL0(layerId,:,:)-273.15
             H = grb_file_new->HGT_P0_L100_GLL0(layerId,:,:)/10.0

             res1@gsnLeftString = stormModel + " " + stormNames(i)
             res1@mpMinLatF = track_yp(i,ifil) -3.5
             res1@mpMaxLatF = track_yp(i,ifil) +3.5
             res1@mpMinLonF = track_xp(i,ifil) -3.5
             res1@mpMaxLonF = track_xp(i,ifil) +3.5

             plotV = gsn_csm_vector_scalar(wks, u, v, T, vres)
             plot = gsn_csm_contour_map(wks, T, res1)
             plot2 = gsn_csm_contour(wks, H, res2)

             overlay(plot,plot2)
             overlay(plot,plotV)

             mres@gsMarkerSizeF = 10.0
             mres@gsMarkerIndex = 16
             mres@gsMarkerThicknessF = 1.0

             mres@gsMarkerColor = "Black"
             pres@gsLineColor = "black"
             line1(i) = gsn_add_polyline(wks,plot,track_xp(i,:),track_yp(i,:),pres)      ; draw the traj
             markers1(i) = gsn_add_polymarker(wks,plot,track_xp(i,:),track_yp(i,:),mres)

             mres@gsMarkerSizeF = 18.0          ; marker size
             mres@gsMarkerIndex = hrind
             ;mres@gsMarkerColor = "white"
             mres@gsMarkerThicknessF = 10.0

             ;markers2_2(i) = gsn_add_polymarker(wks,plot,track_xp(i,ifil)+0.1,track_yp(i,ifil)-0.1,mres)
             ;markers2_3(i) = gsn_add_polymarker(wks,plot,track_xp(i,ifil)-0.1,track_yp(i,ifil)+0.1,mres)
             mres@gsMarkerColor = "black"
             markers2(i) = gsn_add_polymarker(wks,plot,track_xp(i,ifil),track_yp(i,ifil),mres)

             mres@gsMarkerSizeF = 18.0          ; marker size
             mres@gsMarkerColor = "red2"  ;"black" ;deeppink3"
             mres@gsMarkerThicknessF = 4.0
             markers3(i) = gsn_add_polymarker(wks,plot,track_xp(i,ifil),track_yp(i,ifil),mres)

             draw(plot)
             frame(wks)
             system("convert -crop 985x985+18+18 " + figName + " " + figName)
         end if
      end do
   end if
end do

print("end")

end

