function [ data ] = read_pentaCam(filename, catalog )
% read data from pentaCam data file in csv type.
% filename in string.
% catalog in string.
% AWARE the spell!
switch catalog
    case 'FRONT'
        location='B2..EL142';
    case 'BACK'
        location='B144..EL284';
    case 'Cornea'
        % Cornea Front Rh
        % Cornea Front Rv
        % Cornea Front Axis
        % Cornea Front Astig
        % Cornea Front Exz
        location='B313..B317';
    case 'Pachy'
        % Pachy Apex
        % Pachy Min
        % Pachy Min X
        % Pachy Min Y
        location='B318..B321';
    case 'Chamber'
        % Chamber Height
        % Chamber Angle
        location='B322..B323';
    case 'K'
        % K Max (Front)
        % K Max X (Front)
        % K Max Y (Front)
        location='B327..B329';
    case 'Pupil'
        % Pupil Dia
        % XPupil
        % YPupil
        location='B332..B334';
    case 'X'
        location='A337..A592';
    case 'Y'
        location='B337..B592';

end
data=dlmread_nan(filename,';',location);

return


end

