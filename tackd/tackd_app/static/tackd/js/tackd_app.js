$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }

});


var ajaxParse = function() {
    $(".loading").show();
    var url = $("#urltext").val();
    $("#urltext").val("");
    
}

$(document).ready(function() {
    $(".loading").hide();
    $("#parsesubmit").click(ajaxParse);
    $("form").submit(ajaxParse);
    $(window).keydown(function(event){
        if(event.keyCode == 13) {
            event.preventDefault();
            ajaxParse();
            return false;
         }
    });

    $("#new-tack-submit").click(function(event) {
        event.preventDefault();
        var url = $("#tack-url-input").val();
        var description = $("#tack-desc-input").val();
        var board = $("#board-id-hidden").val();
        if (url.trim() === "") {
            alert("You must provide a URL for a new tack");
            return;
        }
        $("#tack-url-input").val("");
        $("#tack-desc-input").val("");
        $.post("/tackd/tack", {
            "url" : url,
            "description" : description,
            "board" : board
        }, function(response) {
            console.log(response);
            (function() {
                console.log("Server returned response: ", response);
                var tack = $("<div>").addClass("tack");
                var imgWrapper = $("<div>").addClass("tack-img-wrapper");
                var img = $("<img>").attr({
                    "src" : response.photo.src,
                    "class" : "tack-img"
                });
                imgWrapper.append(img);
                tack.append(imgWrapper);
                var tackInfo = $("<div>").addClass("tack-info");
                var tackTitle = $("<h4>").addClass("tack-title").html(response.title);
                var tackDesc = $("<span>").addClass("tack-desc").html(description);
    
                var tackTags = $("<div>").addClass("tack-tags");
                var tagBlock = $("<div>").addClass("tag-block");
                tackTags.append(tagBlock);
    
                var tagForm = $("<form>").attr({"id" : "tag-form"}).addClass("tag-form");
                var tagFormInput = $("<input>").attr({
                    "class" : "tag-form-input",
                    "type" : "text",
                    "name" : "tags",
                    "placeholder" : "Tags separated by a space"
                });
                var tagFormButton = $("<input>").attr({
                    "class" : "tag-form-btn",
                    "type" : "button",
                    "value" : "Add Tags"
                }).click(function(event){
                    event.preventDefault();

                    $.post('/tackd/add_tag', {
                        "tack" : response.tackid,
                        "board" : response.boardid,
                        "tags" : tagFormInput.val()
                    }, function(response) {
                        var all_tags = response.tags;
                        tagBlock.empty();
                        for (var k = 0; k < all_tags.length; k++) {
                            var tagSpan = $("<span>").addClass("tack-tag").html(all_tags[k]);
                            $(tagSpan).css("margin", "0 2px");
                            tagBlock.append(tagSpan);
                        }
                    });
                });;
                var tackInputHidden = $("<input>").attr({
                    "type" : "hidden",
                    "name" : "tack",
                    "value" : response.tackid
                });
                var boardInputHidden = $("<input>").attr({
                    "type" : "hidden",
                    "name" : "board",
                    "value" : response.boardid
                });
                tagForm.append(tagFormInput, tagFormButton, tackInputHidden, boardInputHidden);
                tackTags.append(tagForm);
    
                var tackExtras = $("<div>").addClass("tack-extras");
                var tackExtraLike = $("<span>")
                    .addClass("tack-extra")
                    .addClass("tack-"  + response.tackid + "-like")
                    .append($("<i>").addClass("fa fa-heart"))
                    .append($("<span>").addClass("num-extra").html("0"));
    
                var tackExtraComment = $("<span>")
                    .addClass("tack-extra")
                    .addClass("tack-"  + response.tackid + "-comment")
                    .append($("<i>").addClass("fa fa-comment"))
                    .append($("<span>").addClass("num-extra").html("0"));
    
                tackExtras.append(tackExtraLike, tackExtraComment);
    
                var tackComments = $("<div>").addClass("tack-comments")
                                             .addClass("tack-" + response.tackid + "-comments");
                var commentBlock = $("<div>").addClass("comment-block");
                tackComments.append(commentBlock);
    
                var addComment = $("<div>").addClass("add-comment");
                var newCommentForm = $("<form>").attr({
                    "class": "new-comment-form",
                    "id" : "new-comment-form"
                });
                var tackCommentInput = $("<input>").attr({
                    "class" : "tack-comment-input",
                    "type" : "text",
                    "name" : "text",
                    "placeholder" : "Add a comment..."
                });
                var tackCommentButton = $("<input>").attr({
                    "class" : "tack-comment-btn",
                    "type" : "button",
                    "value" : "Comment"
                }).click(function(event) {
                    event.preventDefault();
                    var text = tackCommentInput.val();
                    if (text.trim() === '') {
                        alert("Your comment is empty :(");
                        return;
                    }
                    $.post('/tackd/add_comment', 
                    {'text' : text, 'tack' : response.tackid, 'board' : response.boardid}, 
                    function(response) {
                        var div = commentBlock;
                        var comment = $("<div>").addClass("tack-comment");
                        var val = "<b>" + response.username + "</b> commented: &ldquo;" + text + "&rdquo;"
                        comment.html(val);
                        div.append(comment);
                    });
                })

                newCommentForm.append(tackCommentInput, tackCommentButton, tackInputHidden, boardInputHidden);
                addComment.append(newCommentForm);
                tackComments.append(addComment);
    
                tackInfo.append(tackTitle, tackDesc, tackTags, tackExtras, tackComments);
                tack.append(tackInfo);
                $(".tacks").append(tack);
            })();
        });
    });

    var commentSections = $(".add-comment");
    var commentDivs = $(".comment-block");
    var tackTags = $(".tack-tags");
    var board = $("#board-id-hidden").val();
    for (var i = 0; i < commentSections.length; i++) {
        (function() {
            var j = i;
            var tackDiv = tackTags.children(".tag-block");
            var currentSection = commentSections.eq(j);
            var currentForm = currentSection.children(".new-comment-form")
            var tagForm = tackTags.eq(j).children("#tag-form");
            var tackid = currentForm.children("input[name='tack']").val();
            var thisTack = tackTags.eq(j);
            tagForm.children(".tag-form-btn").click(function(event) {
                event.preventDefault();
                var tagString = tagForm.children(".tag-form-input").val().trim();
                tagForm.children(".tag-form-input").val("");
                $.post('/tackd/add_tag', {
                    "tack" : tackid,
                    "board" : board,
                    "tags" : tagString
                }, function(response) {
                    var all_tags = response.tags;
                    var tagBlock = thisTack.children(".tag-block")
                    tagBlock.empty();
                    for (var k = 0; k < all_tags.length; k++) {
                        var tagSpan = $("<span>").addClass("tack-tag").html(all_tags[k]);
                        $(tagSpan).css("margin", "0 2px");
                        tagBlock.append(tagSpan);
                    }
                });
            });
            currentForm.children(".tack-comment-btn").click(function(event) {
                event.preventDefault();
                var text = currentForm.children("input[name='text']").val();
                if (text.trim() === '') {
                    alert("Your comment is empty :(");
                    return;
                }
                currentForm.children("input[name='text']").val("");
                $.post('/tackd/add_comment', 
                    {'text' : text, 'tack' : tackid, 'board' : board}, 
                    function(response) {
                        console.log(response);
                        var div = commentDivs.eq(j);
                        var comment = $("<div>").addClass("tack-comment");
                        var val = "<b>" + response.username + "</b> commented: &ldquo;" + text + "&rdquo;"
                        comment.html(val);
                        div.append(comment);
                    });
            });
        })();
    }

    var allComments = $(".tack-comment");
    for (var i = 0; i < allComments.length; i++) {
        (function () {
            var j = i;
            var thisComment = allComments.eq(j);
            var thisUsername = thisComment.children("b");
            thisUsername.click(function(event) {
                event.preventDefault();
                var userProfileWrapper = $("<div>").attr({"id" : "userprofile-wrapper"});
                var userProfileBox = $("<div>").attr({"id" : "userprofile-box"});
                var userProfileClose = $("<div>").attr({"id" : "userprofile-close"})
                    .append($("<i>").addClass("fa").addClass("fa-times"))
                    .click(function(event) {
                        event.preventDefault();
                        userProfileWrapper.fadeOut(300, function() {
                            userProfileWrapper.remove();
                        });
                    });
                var userProfilePhoto = $("<div>").attr({"id" : "userprofile-photo"});
                var userProfileName = $("<div>").attr({"id": "userprofile-name"})
                    .html("@" + thisUsername.text());
                var userProfileBio = $("<div>").attr({"id" : "userprofile-bio"});
                userProfileWrapper.append(userProfileBox.append(userProfileClose, 
                                                                userProfilePhoto, 
                                                                userProfileName, 
                                                                userProfileBio));
                $.get('/tackd/user-info/' + thisUsername.text(), function(response) {
                    console.log(response);
                    var profile_url = response["profile_image_url"];
                    profile_url = profile_url.replace("_normal", "");
                    var bio = response["description"];
                    $("#userprofile-photo")[0].style.backgroundImage = "url('" + profile_url + "')";
                    userProfileBio.html(bio);
                });
                userProfileWrapper.hide();
                $("body").prepend(userProfileWrapper);
                userProfileWrapper.fadeIn(300);
            });
        })();
    }

    $("input[name='username']").typeahead({
        name: 'users',
        prefetch: '/tackd/all_users'
    });

    $("img").one('load', function() {
        if ($(".tack-img-wrapper").css("width")) {
            var max_width = $(".tack-img-wrapper").css("width").replace("px", "") * 2;
            if ($(this).css("width").replace("px", "") < max_width) {
                $(this).css("margin", "0");
            }
        }
    }).each(function() {
        if(this.complete) $(this).load();
    });
    
    var notifications = {};
    var updateNotifications = function() {
        $.post('/tackd/notifications', function(response) {
            var count = 0
            var notificationList = $("#notification-list");
            notificationList.empty();
            for (var i = 0; i < response.length; i++) {
                count++;
                notification = response[i];
                notificationList.append($("<span>").addClass("notification-cell").html(notification['text']));
            }
            if (count === 0) {
                $(".notification-badge").hide();
            } else {
                $(".notification-badge").show(); 
            }
            $(".notification-badge").html("" + count)
        });
    }
    updateNotifications();

    $(".nav-button .fa-bell-o").click(function() {
        $("#notification-box").toggle(100, function() {

        });
    });

    // check for notifications every 15 second
    setInterval(updateNotifications, 1000 * 15);

    $(".firstbox").click(function() {
        $(".darkness").show();
    });

    $(".lightcancel").click(function() {
        $(".darkness").hide();
    });

    $("#board-submit").click(function() {
        document.getElementById('createform').submit();
    });

    $(".addimage").click(function(){
        $("#new-board-photo").click();
    });
});