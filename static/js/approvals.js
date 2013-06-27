function approve(id) {
    baseapprover(id, "approved");
}

function deny(id) {
    baseapprover(id, "denied");
}

function baseapprover(id, status) {
    $.ajax({
        type: "POST",
        url: CONFIG.APPROVAL_URL,
        data: {
            status: status,
            pending_id: id
        },
        success: function(data) {
            location.reload();
        }
    });

}
