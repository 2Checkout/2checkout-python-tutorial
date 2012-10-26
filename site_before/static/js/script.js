$(document).ready(function(){
	
		$('#register-form').validate({
	    rules: {
	      email: {
	        required: true,
	        email: true
	      },
	      username: {
	        minlength: 2,
	        required: true
	      },
	      password: "required",
				confirm: {
					equalTo: "#password"
				}
	    },
	    highlight: function(label) {
				$(label).closest('.control-group').addClass('error');
	    },
	    success: function(label) {
				label
					.text('OK!').addClass('valid')
					.closest('.control-group').addClass('success');
	    }
	  });
	  
});