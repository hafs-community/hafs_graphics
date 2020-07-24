load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"

procedure placeAMarkerLineLegend(wks, legend, x, y, w, h, fontHeight, markIdxs, color, size, lThickness, mThickness)  
begin
  lgres = True
  lgres@lgItemType = "MarkLines"
  lgres@vpWidthF = w 
  lgres@vpHeightF = h
  lgres@lgLabelOffsetF = 0.08
  lgres@lgPerimOn = False
  lgres@lgDashIndex = 0 ;(/0,0,0,0,0,0,0/)
  lgres@lgLabelFontHeightF = fontHeight
  lgres@lgLineColor = color 
  lgres@lgMarkerColor = color 
  lgres@lgLineThicknessF = lThickness
  lgres@lgMarkerSizeF = size 
  lgres@lgMarkerThicknessF = mThickness 
  lgres@lgMarkerIndex   = markIdxs 
  lgres@lgMonoMarkerIndex     = True
  lgres@lgMonoLineThickness   = True
  lgres@lgMonoMarkerThickness = True
  lgres@lgMonoMarkerSize      = True
  lgres@lgMonoMarkerColor      = True
  lgres@lgMonoLineColor   = True
  legend_label = (/legend/)
  gsn_legend_ndc(wks,1,legend_label, x, y, lgres) 
end 

procedure placeAMarkerLegend(wks, legend, x, y, w, h, fontHeight, markIdxs, color, size, mThickness)  
begin
  lgres = True
  lgres@lgItemType = "Markers"
  lgres@vpWidthF = w 
  lgres@vpHeightF = h
  lgres@lgLabelOffsetF = 0.08
  lgres@lgPerimOn = False
  lgres@lgLabelFontHeightF = fontHeight
  lgres@lgMarkerColor = color 
  lgres@lgMarkerSizeF = size 
  lgres@lgMarkerThicknessF = mThickness 
  lgres@lgMarkerIndex   = markIdxs 
  lgres@lgMonoMarkerIndex     = True
  lgres@lgMonoMarkerThickness = True
  lgres@lgMonoMarkerSize      = True
  lgres@lgMonoMarkerColor     = True
  legend_label = (/legend/)
  gsn_legend_ndc(wks,1,legend_label, x, y, lgres) 
end 

