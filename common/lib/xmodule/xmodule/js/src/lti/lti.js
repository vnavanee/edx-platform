window.LTI = function (element){
    var form = element.find('#ltiLaunchForm'),
        frame = element.find('#ltiLaunchFrame');

    console.log('form = ', form);
    console.log('frame = ', frame);

    $(document).ready(init);

    return;

	function init() {
        console.log('We are in window.LTI function');
        console.log('element = ', element);

        form.submit();

        frame.width(400).height(600);
    }
}
