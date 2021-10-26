
function b4_class(value) {
    const class_map = {
        'error': 'danger',
        '400': 'danger',
        '500': 'danger',
        'success': 'success',
        '200': 'success',
        'warning': 'warning',
        'info': 'info',
        'debug': 'secondary',
    }
    return class_map[value.trim().toLowerCase()] || 'primary'
}

function getErrorType(value){
    const error_map = {
        'danger': 'Error',
        'success': 'Success',
        'warning': 'Warning',
        'info': 'Info',
        'secondary': 'Info',
    }
    return error_map[value.trim().toLowerCase()] || 'Info'
}

function showToast(message, type) {
    let random_number = Math.floor(Math.random() * 1000)
    let toast_head = getErrorType(type)

    const toast = `
            <div id="toast-${random_number}" class="toast bg-${type} slide-in-blurred-right" data-autohide="false">
                <div class="toast-header">
                    <strong class="mr-auto text-${type}">${toast_head}: </strong>
                    <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" onclick="$('#toast-${random_number}').remove()">&times;</button>
                </div>
                <div class="toast-body text-light">
                    ${message}
                </div>
            </div>
    `
    const toast_area = $('#toast-area');
    toast_area.html(toast)
    $('#toast-' + random_number).toast('show')
}