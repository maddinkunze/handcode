width = 33;
height = 20;
pendiam = 8;

bdiam = 4;
bheight = 25;

S_excentricity = 0.25;
S_tolerance = 0.01;
S_wallX = 0.5 * (width - S_excentricity * (width - pendiam)) + S_tolerance;
S_btolerance = 0.4;
S_noffset = 3;

module penholder(cwidth, clength, cheight, pdiam, swidth, lwidth, excentricity=0) {
  _tolerance = 0.01;
  linear_extrude(cheight, convexity=4) difference() {
    translate([0, 0.5 * excentricity * (clength - pdiam)]) square([cwidth, clength], center=true);
    circle(d=pdiam, $fn=50);
    square([2*(cwidth+_tolerance), swidth], center=true);
    
    _olipX = cwidth/2 + _tolerance;
    _ilipX = (pdiam/2) * cos(asin((lwidth + swidth/2) / (pdiam/2))) + lwidth;
    _olipY = swidth/2;
    polygon([[-_olipX, _olipY+lwidth], [-_olipX+lwidth, _olipY], [-_olipX+lwidth, -_olipY], [-_olipX, -_olipY-lwidth]]);
    polygon([[_olipX, _olipY+lwidth], [_olipX-lwidth, _olipY], [_olipX-lwidth, -_olipY], [_olipX, -_olipY-lwidth]]);
    polygon([[_ilipX, _olipY], [_ilipX-lwidth, _olipY+lwidth], [-_ilipX+lwidth, _olipY+lwidth], [-_ilipX, _olipY], [-_ilipX, -_olipY], [-_ilipX+lwidth, -_olipY-lwidth], [_ilipX-lwidth, -_olipY-lwidth], [_ilipX, -_olipY]]);
  }
}

module nutandbolt(bdiam, blength, bhead, ndiam, nheight, noffset=0) {
  _tolerance = 0.01;
  _bheadlength = (bhead - bdiam) / 2;
  union() {
    cylinder(_bheadlength, d1=bhead, d2=bdiam, center=false, $fn=50);
    translate([0, 0, _bheadlength-_tolerance]) cylinder(blength - _bheadlength, d=bdiam, $fn=50);
    translate([0, 0, blength - nheight - noffset]) cylinder(nheight, d=ndiam, $fn=6);
  }
}

difference() {
  penholder(width, width, height, pendiam, 0.2*pendiam, 0.1*pendiam, S_excentricity);
  translate([0.3*width, -S_wallX, height/2]) rotate([-90, 0, 0]) nutandbolt(bdiam+S_btolerance, bheight+S_noffset, 2*bdiam, 2*bdiam+S_btolerance, 0.8*bdiam, S_noffset);
  translate([-0.3*width, -S_wallX, height/2]) rotate([-90, 0, 0]) nutandbolt(bdiam+S_btolerance, bheight+S_noffset, 2*bdiam, 2*bdiam+S_btolerance, 0.8*bdiam, S_noffset);
}
