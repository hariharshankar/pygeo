	var validForm;
	var firstError;

	function validate() {
		validForm = true;
		var ele = document.forms[0].elements;
		var emailregex = /email/i;
		var usernameregex = /username/i;
		var passwordregex = /password/i;
		var state = false;
		for ( var i=0; i<ele.length; i++ ) {
			if ( ele[i].className == 'require' ) {
				if ( !ele[i].value ) {
					validation_error ( ele[i], "This is a required field" );
				}
			}
	        if ( ele[i].name.match ( emailregex ) ) { 
				if ( !validateEmail ( ele[i].value ) ) {
					validation_error ( ele[i], "Please enter a valid email address." );
				}
	        }
			if ( ele[i].name.match ( usernameregex ) ) {
				if ( !validateUsername ( ele[i].value ) ) {
					validation_error ( ele[i], "Please read the instructions on username." );
				}
			}
			if ( ele[i].name.match ( passwordregex ) ) {
				if ( !validatePassword ( ele[i].value ) ) {
					validation_error ( ele[i], "Please read the instructions on password." );
				}
			}
			if ( ele[i].name.match ( /state/i ) && !ele[i].name.match ( /_sys/i ) ) {
				state = true;
			}
		}
		if ( !state ) {
			alert ("Please choose your country first and select your state from the resulting menu.");
			validForm = false;
		}
		if ( firstError )
			firstError.focus();
		return validForm;	
 	}

	function validateForm() {
		validForm = true;
		console.log(document.forms)
		var ele = document.forms[0].elements;
		
		var yrregex = /_yr/i;
		var nbrregex = /_nbr/i;
		var dtregex = /_dt/i;

		var state = false;
		//alert(document.forms[1].value);
		for ( var i=0; i<ele.length; i++ ) {
			if ( ele[i].className == 'require' ) {
				if ( !ele[i].value ) {
					validation_error ( ele[i], "This is a required field" );
				}
			}
	        if ( ele[i].name.match ( yrregex ) ) { 
				if ( !validateYear ( ele[i].value ) ) {
					validation_error ( ele[i], "Year expected in 'YYYY' format." );
				}
	        }
			if ( ele[i].name.match ( nbrregex ) ) {
				if ( !validateNumber ( ele[i].value ) ) {
					validation_error ( ele[i], "Number expected." );
				}
			}
			if ( ele[i].name.match ( dtregex ) ) {
				if ( !validateDate ( ele[i].value ) ) {
					validation_error ( ele[i], "Date should be in 'YYYY-MM-DD' format." );
				}
			}
			if ( ele[i].name.match ( /state/i ) && !ele[i].name.match ( /_sys/i ) ) {
				state = true;
			}
		}
		
		if ( firstError )
			firstError.focus();
        if (validForm) {
            var res = confirm( "Are you sure you want to submit?" );
            if( res )
                return validForm;
            else 
                return false;
        }
        else 
            return false;
 	}

	function validation_error ( element, errmsg ) {
		validForm = false;
		if ( element.hasError ) 
			return;
		var errele = document.createElement ( 'span' );
		errele.className = 'ui-state-error ui-corner-all';
		errele.innerHTML = errmsg;
		element.parentNode.appendChild ( errele );
		element.hasError = errele;
		element.onchange = removeError;
		if ( !firstError )
			firstError = element;
	}

	function removeError() {
		this.parentNode.removeChild ( this.hasError );
		this.hasError = null;
		this.onchange = null;
	}

	function validateUsername ( username ) {
		var regex = /\w{6,}/;
		if ( username.match ( regex ) )
			return true;
		else
			return false;
	}

	function validatePassword ( password ) {
		var regex = /\w{8,}/;
		if ( password.match ( regex ) )
			return true;
		else
			return false;
	}

	function validateEmail ( email ) {
		var regex = /[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:[A-Z]{2}|com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|edu)\b/;
		if ( email.match ( regex ) )
			return true;
		else
			return false;
	}
	
	function validateNumber ( number ) {
		var regex = /^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$/;
		if ( number.match ( regex ) )
			return true;
        else if( number.match( /^$/ ) )
            return true;
		else
			return false;
	}

	function validateYear ( year ) {
		var regex = /^\s*$|^[0-9]{4}$/;
		if ( year.match ( regex ) )
			return true;
		else
			return false;
	}

	function validateDate ( date ) {
		var regex = /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/;
        if ( !date ) 
            return true;
		if ( date.match ( regex ) )
			return true;
		else
			return false;
	}

