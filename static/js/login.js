function validateForm() {
    var password = document.getElementById("signup-password").value;
    var confirmPassword = document.getElementById("signup-confirm-password").value;

    if (password !== confirmPassword) {
        alert("Passwords do not match.");
        document.getElementById("signup-password").value="";
        document.getElementById("signup-confirm-password").value="";
        return false;
    }
    return true;
}

$(document).ready(function() {
    $("#signup-form").hide();
    $("#logh").click(function() {
        $("#signup-form").hide();
        $("#login-form").show();
        $("#logh").addClass("active");
        $("#signh").removeClass("active");
    });
    $("#signh").click(function() {
        $("#login-form").hide();
        $("#signup-form").show();
        $("#signh").addClass("active");
        $("#logh").removeClass("active");
    });
});
