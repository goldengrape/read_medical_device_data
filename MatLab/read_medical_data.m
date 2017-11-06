function [ data ] = read_medical_data(data_file, catalog,json_data_file )
% Uni read medical data function
% You need to install JSONlab first:
% https://cn.mathworks.com/matlabcentral/fileexchange/33381-jsonlab--a-toolbox-to-encode-decode-json-files
% eg. json_data_file='../medical_device_data/sirius.json'

catalog_dict=loadjson(json_data_file);
location=catalog_dict.(catalog);
data=dlmread(data_file,';',location);

return
end