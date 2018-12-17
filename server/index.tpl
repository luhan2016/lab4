% include('server/board_frontpage_header_template.tpl')
% include('server/boardcontents_template.tpl',board_title=board_title,vote_dict=vote_dict, f_result=f_result)
% include('server/board_frontpage_footer_template.tpl',members_name_string=members_name_string)