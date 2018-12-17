<!-- this place will show the actual contents of the blackboard. 
It will be reloaded automatically from the server -->
<div id="boardcontents_placeholder">
	<!-- The title comes here -->
	<div id="boardtitle_placeholder" class="boardtitle">{{board_title}}</div>
    <input type="text" name="id" value="Vessle" readonly>
    <input type="text" name="entry" value="Vote" size="70%%" readonly>
    % for vesselID, vote_Value in vote_dict:
		<form class="entryform" target="noreload-form-target" method="post" action="/vote/attack/{{vesselID}}">
			<input type="text" name="id" value="{{vesselID}}" readonly disabled> <!-- disabled field won’t be sent -->
			<input type="text" name="entry" value="{{vote_Value}}" size="70%%">
		</form>
    %end
    <input type="text" name="finalresult" value="Final result is: {{f_result}}" readonly>
</div>
  