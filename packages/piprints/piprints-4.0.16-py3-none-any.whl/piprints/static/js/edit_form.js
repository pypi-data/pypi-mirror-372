function setup_list_autocompletion() {
  $("input.autocomplete_list").autocomplete({
     minlength: 0,
	   source: function(request, response) {
       url = $(this.element).attr('autocomplete_url');
	     $.ajax({
		      "url": url,
		      dataType: "json",
		      data: {},
		      success: function(data) {response(data.lst);}
	     });
	   }
   });
   $("input.autocomplete_list").focus(function(){
     /* force displaying list even if no key is pressed */
     $(this).autocomplete("search", minlength=0);
   });
}

function setup_autocompletion() {
    $("input.autocomplete.lastname").autocomplete({
	source: function(request, response) {
	    $.ajax({
		url: "/autocomplete/lastname/",
		dataType: "json",
		data: {
		    lastname: request.term
		},
		success: function(data) {response(data);}
	    });
	},
	close: function(event, ui) {
	    var val = $(this).val();
	    var i = val.indexOf(',');
	    if (i!== -1) {
		var lastname = val.substring(0,i).trim();
		var firstname = val.substring(i+1).trim();
		$(this).val(lastname);
		$(this).parent().parent().find("input.firstname").val(firstname);
		$(this).parent().parent().next().find("input")[0].focus();
	    }
	}
    });

    $("input.autocomplete.firstname").autocomplete({
	source: function(request, response) {
	    $.ajax({
		url: "/autocomplete/firstname/",
		dataType: "json",
		data: {
		    lastname: $(this.element).parent().parent().find("input.lastname").val(),
		    firstname: request.term
		},
		success: function(data) {response(data);}
	    });
	}});
}

function adderClick() {
    var row=$(this).parent().parent().prev();
    var x=row.clone();
    x.find("input").val("");
    row.after(x);
    x.find("input")[0].focus();
    setup_autocompletion();
}

$(function() {
    $(".adder").click(adderClick);
    setup_autocompletion();
    setup_list_autocompletion();
});
