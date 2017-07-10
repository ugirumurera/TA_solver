clear 
close all

root = fileparts(mfilename('fullpath'));

% strucutres
node_struct = struct('id',nan,'x',nan,'y',nan);
link_struct = struct('id',nan,'start_node',nan,'end_node',nan,'full_lanes',nan,'roadparam',nan);
road_param_struct = struct('id',nan,'capacity',nan,'speed',nan,'jam_density',nan);

%% load network
fid = fopen(fullfile(root,'ChicagoRegional_net.txt'));
line = fgetl(fid);
while line(1)~='~'
    line = fgetl(fid);
end
raw_links=textscan(fid,'%d%d%d%f%d%f%d%d%d%d%s');
fclose(fid);

% read parameters
num_links   = numel(raw_links{1});
start_nodes = raw_links{1};
end_nodes   = raw_links{2};
capacity    = double(raw_links{3});              % veh/hr -> veh/hr
link_lengths = double(raw_links{4})*1609.34;     % miles -> meters
speed       =  double(raw_links{8})*1.6;         % miles/hr -> km/hr
clear raw_links

[unique_params,~,link_params] = unique([capacity speed],'rows');
road_params = repmat(road_param_struct,size(unique_params,1),1);
for i=1:size(unique_params,1)
    road_params(i).id = i;
    road_params(i).capacity = unique_params(i,1);  
    road_params(i).speed = max([25 unique_params(i,2)]);   % minimmum of 25 km/hr
    road_params(i).jam_density = 100;                      % veh/km
end

links = repmat(link_struct,1,num_links);
for i=1:num_links
    links(i).id = i;
    links(i).start_node = start_nodes(i);
    links(i).end_node = end_nodes(i);
    links(i).length = link_lengths(i);
    links(i).full_lanes = 1;
    links(i).roadparam = link_params(i);
end

%% load nodes
fid = fopen(fullfile(root,'ChicagoRegional_node.txt'));
line = fgetl(fid);
raw_nodes=textscan(fid,'%d%d%d');
fclose(fid);

nodes = repmat(node_struct,1,numel(raw_nodes{1}));
for i=1:numel(raw_nodes{1})
    nodes(i).id = raw_nodes{1}(i);
    nodes(i).x = raw_nodes{2}(i)*0.3048;       % ft -> meters
    nodes(i).y = raw_nodes{3}(i)*0.3048;       % ft -> meters
end
clear raw_nodes

%% load trips
% tic
% fid = fopen(fullfile(root,'ChicagoRegional_trips.txt'));
% c=0;
% while ~feof(fid)
%     line = fgetl(fid);
%     
%     % find next Origin
%     while isempty(strfind(line,'Origin'))
%         line = fgetl(fid);
%     end
%     
%     % read the data
%     raw_links=textscan(fid,'%d:%f;');
%     
%     c = c + length(raw_links{1});
%     
%     
% end
% 
% fclose(fid);
% disp(toc)

%% construct beats network
sb = ScenarioBuilder;
sb.add_nodes(nodes);
sb.add_links(links);
sb.add_roadparams(road_params);
sb.write('chicago_regional.xml')




