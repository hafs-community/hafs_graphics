function getCategoryColor(w)
begin
     color = "(/0.0, 0.0, 0.0/)"
     if (w .ge. 34 .and. w .lt. 64)  then
        color="(/0.0, 1.00, 0.957/)"
      else if (w .ge. 64 .and. w .lt. 83) then
         color="(/1.00, 1.00, 0.8/)"
      else if (w .ge. 83 .and. w .lt. 96)
         color="(/1.00, 0.901, 0.459/)"
      else if (w .ge. 96 .and. w .lt. 113)
         color="(/1.00, 0.757, 0.251/)"
      else if (w .ge. 113 .and. w .lt. 137)
         color="(/1.00, 0.561, 0.125/)"
      else if (w .ge. 137 )
         color="(/1.00, 0.376, 0.376/)"
      else if (w .lt. 34)
         color="(/0.369, 0.730, 1.00/)"
      end if
      end if
      end if
      end if
      end if
      end if
      end if
      return(color)
end

function catColor(w)
begin
  color = "white"
  if (w .lt. 34.) then
    color  = "skyblue2"
  end if
  if (w .ge. 34.) then
    color  = "springgreen2"
  end if
  if (w .ge. 64.) then
    color  = "darkorange2"
  end if
  if (w .ge. 83.) then
    color  = "orangered2"
  end if
  if (w .ge. 96.) then
    color  = "firebrick2"
  end if
  if (w .ge. 113.) then
    color  = "deeppink2"
  end if
  if (w .ge. 137.) then
    color  = "deeppink4"
  end if
  return(color)
end
