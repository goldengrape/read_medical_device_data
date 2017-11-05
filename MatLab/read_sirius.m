function [ data ] = read_sirius(filename, catalog )
% read data from Sirius Corneal data file in csv type.
% filename in string.
% catalog in string.
% AWARE the spell!
switch catalog
    case 'Radii'
        location='A2..AE2';
    case 'CornealThickness'
        location='A4..IV34';
    case 'ElevationAnterior'
        location='A36..IV66';
    case 'ElevationPosterior'
        location='A68..IV98';
    case 'RefractiveEquivalentPower'
        location='A100..IV130';
    case 'RefractiveFrontalPowerAnterior'
        location='A132..IV162';
    case 'RefractiveFrontalPowerPosterior'
        location='A164..IV194';
    case 'SagittalAnterior'
        location='A196..IV226';
    case 'SagittalPosterior'
        location='A228..IV258';
    case 'TangentialAnterior'
        location='A260..IV290';
    case 'TangentialPosterior'
        location='A292..IV322';
end
data=dlmread(filename,';',location);
return
end
