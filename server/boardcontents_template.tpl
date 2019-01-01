<!-- this place will show the actual contents of the blackboard. 
It will be reloaded automatically from the server -->
<div id="boardcontents_placeholder">
	<!-- The title comes here -->
	<div id="boardtitle_placeholder" class="boardtitle">{{board_title}}</div>
    <input type="text" name="id" value="Vessle" readonly>
    <input type="text" name="entry" value="Vote" size="70%%" readonly>
    % for vesselID, vote_Value in vote_dict:
		<form class="entryform" target="noreload-form-target" method="post" action="/vote/result/{{vesselID}}">
			<input type="text" name="id" value="{{vesselID}}" readonly disabled> <!-- disabled field won’t be sent -->
			<input type="text" name="entry" value="{{vote_Value}}" size="70%%">
		</form>
    %end
	</br>

    <input type="text" name="id" value="Vessle" readonly>
    <input type="text" name="entry" value="Vote Vector" size="70%%" readonly>
    % for vesselID, vote_vector in vote_vector_dict:
		<form class="entryform" target="noreload-form-target" method="post" action="/vote/result/{{vesselID}}">
			<input type="text" name="id2" value="{{vesselID}}" readonly disabled> 
			<input type="text" name="entry2" value="{{vote_vector}}" size="70%%">
		</form>
    %end
	</br>

    <input type="text" name="final_vector" value="result vector is: " readonly>
	<input type="text" name="f_vector" value="{{final_result_vector}}" size="70%%">
	</br>
    <input type="text" name="final_result" value="final result is:" readonly>
	<input type="text" name="f_result" value="{{f_result}}" size="70%%">
</div>
  