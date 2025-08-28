${make_header('lua')}
  % for feature in render_utils.get_features(root):
% if project_name != 'dft' and project_name != 'debug':
require 'plugin.features.${feature}'
% else:
require 'plugin.${project_name}.features.${feature}'
% endif
  % endfor