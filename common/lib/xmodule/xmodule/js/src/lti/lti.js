window.LTI = function (element){
    var form = element.find('#ltiLaunchForm'),
          frame = element.find('#ltiLaunchFrame');

    $(document).ready(init);

    return;

    function init() {
        form.submit();
        frame.width('100%').height(800);
    }
}
