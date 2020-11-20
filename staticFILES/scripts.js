function prepareDocument(){
//code to prepare page here.
    jQuery("form#search").submit(function(){
        text = jQuery("#id_q").val();
        if (text == "" || text == "Search"){
        // if empty, pop up alert
        alert("Enter a search term.");
        // halt submission of form
        return false;
        }
    });

    jQuery("#submit_review").click(addProductReview);
    jQuery("#review_form").addClass('hidden');
    jQuery("#add_review").click(slideToggleReviewForm);
    jQuery("#add_review").addClass('visible');
    jQuery("#cancel_review").click(slideToggleReviewForm);
    jQuery("#id_q").keyup(autoresult);

    // toggles visibility of "write review" link
    // and the review form.
    function slideToggleReviewForm(){
        jQuery("#review_form").slideToggle();
        jQuery("#add_review").slideToggle();
    }

    function addProductReview(){
        // build an object of review data to submit
        var review = {
            title: jQuery("#id_title").val(),
            content: jQuery("#id_content").val(),
            rating: jQuery("#id_rating").val(),
            slug: jQuery("#id_slug").val(),
            csrfmiddlewaretoken: jQuery("#reviewcsrf").val()};
        // make request, process response
        jQuery.post("/review/product/add/", review,
            function(response){
                jQuery("#review_errors").empty();
                // evaluate the "success" parameter
                if(response.success == "True"){
                    // disable the submit button to prevent duplicates
                    jQuery("#submit_review").attr('disabled','disabled');
                    // if this is first review, get rid of "no reviews" text
                    jQuery("#no_reviews").empty();
                    // add the new review to the reviews section
                    jQuery("#reviews").prepend(response.html).slideDown();
                    // get the newly added review and style it with color
                    new_review = jQuery("#reviews").children(":first");
                    new_review.addClass('new_review');
                    // hide the review form
                    jQuery("#review_form").slideToggle();
                }
                else{
                    // add the error text to the review_errors div
                    jQuery("#review_errors").append(response.html);
                }
            }, "json");
    }

//tagging functionality to prepareDocument()
    jQuery("#add_tag").click(addTag);
    jQuery("#id_tag").keypress(function(event){
        if (event.keyCode == 13 && jQuery("#id_tag").val().length > 2){
            addTag();
            event.preventDefault();
        }
    });

    function addTag(){
        tag = { tag: jQuery("#id_tag").val(),
            slug: jQuery("#id_slug").val(),
            csrfmiddlewaretoken: jQuery("#tagcsrf").val()};
        jQuery.post("/tag/product/add/", tag, function(response){
            if (response.success == "True"){
                jQuery("#tags").empty();
                jQuery("#tags").append(response.html);
                jQuery("#id_tag").val("");
            }
        }, "json");
    }

    var rating = $("#rating").click(ratingvalue);
    function ratingvalue(e){
      var star1 = $("#id_rating1").val();
      var star2 = $("#id_rating2").val();
      var star3 = $("#id_rating3").val();
      var star4 = $("#id_rating4").val();
      var star5 = $("#id_rating5").val();
      var target = $(e.target);

      if(star1 == 1 && target.val() == star1){
            star = star1
            $("#id_rating").val(star)
            return star;
         }
      if(star2 == 2 && target.val() == star2){
            star = star2
            $("#id_rating").val(star)
            return star;
         }
      if(star3 == 3 && target.val() == star3){
            star = star3
            $("#id_rating").val(star)
            return star;
         }
      if(star4 == 4 && target.val() == star4){
            star = star4
            $("#id_rating").val(star)
            return star;
         }
      if(star5 == 5 && target.val() == star5){
            star = star5
            $("#id_rating").val(star)
            return star;
         }
    };

    function statusBox(){
        jQuery('<div id="loading">Loading...</div>')
        .prependTo("#main")
        .ajaxStart(function(){jQuery(this).show();})
        .ajaxStop(function(){jQuery(this).hide();})
    }

    // auto search suggestions
    function autoresult() {
        var q = jQuery("#id_q").val().toLowerCase();
        if(q == ''){
            jQuery('#slist').html("<li id=\"pitem\" style=\"display: none;\"><img id=\"simage\" /></li>");
        }
        if(q.length > 0){
            $.ajax({
                url:'/search/autoresults/',
                method: 'GET',
                data: {
                    'q': q
                },
                success: function(data){
                    jQuery('#slist').html('');
                    jQuery('#slist').append(data);
                },
                dataType: 'text'
            });
        }else{
            jQuery('#slist').html("<li id=\"pitem\" style=\"display: none;\"><img id=\"simage\" /></li>")
        }
    }

    // click on auto suggest li text
    jQuery("#slist").click(function(event){
      var target = jQuery(event.target);
      jQuery("#id_q").val(target.text());
      jQuery("#slist").html('<li id=\"pitem\" style=\"display: none;\"><img id=\"simage\" /></li>');
    });

    // click on auto suggest image
    $("#slist").click(function(event){
      var target = $(event.target);
      $("#id_q").val(target.next().text());
      $("#slist").html('<li id=\"pitem\" style=\"display: none;\"><img id=\"simage\" /></li>')
    });

    $("#slist").click(function(){
        $(this).data('clicked', true)
    });

    $(document.body).click(function(event){
        if( $("#slist").data('clicked') ){
            $("#id_q").val($(event.target).text())
            $("#slist").data('clicked', false)
         }else{
            $("#slist").html('<li id=\"pitem\" style=\"display: none;\"><img id=\"simage\" /></li>');
         };
    });

    $(document).keydown(TabExample);
    function TabExample(evt) {
      var evt = (evt) ? evt : ((event) ? event : null);
      var tabkey = 9;
      if(evt.keyCode == tabkey) {
        $("#slist").html('<li id=\"pitem\" style=\"display: none;\"><img id=\"simage\" /></li>');
      }
    }

    $("#id_name").change(slugvalue);
    $("#id_name").keydown(slugvalue);
    $("#id_name").keyup(slugvalue)
    function slugvalue(){
      var name = $("#id_name");
      var slug = name.val();
      var slug = slug.replace(" ", "-").toLowerCase();
      var slug = slug.replace(/[&\/\\#, @^!\`\[\]+()$~%.'":*?<>{}]/g, '').toLowerCase();
      var slugvalue1 = $("#id_slug").val(slug);
      slugvalue1;
      /*var slugvalue.val(slug);*/
    }

}
jQuery(document).ready(prepareDocument);