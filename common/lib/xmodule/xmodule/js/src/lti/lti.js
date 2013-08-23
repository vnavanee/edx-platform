window.LTI = (function () {
    var LTI;

    // Function LTI()
    //
    // The LTI module constructor. It will be called by XModule for any
    // LTI module DIV that is found on the page.
    LTI = function (element) {
        $(document).ready(function () {
            LTI.init(element);
        });
    }

    // Function init()
    //
    // Initialize the LTI iframe.
    LTI.init = function (element) {
        var form, frame, iDoc, errorMessage;

        // In cms (Studio) the element is already a jQuery object. In lms it is
        // a DOM object.
        //
        // To make sure that there is no error, we pass it through the $()
        // function. This will make it a jQuery object if it isn't already so.
        element = $(element);

        form = element.find('#ltiLaunchForm');
        frame = element.find('#ltiLaunchFrame');

        // If the Form's action attribute is set (i.e. we can perform a normal
        // submit), then we submit the form and make it big enough so that the
        // received response can fit in it.
        if (form.attr('action')) {
            form.submit();
            frame.width('100%').height(800);
        }

        // If no action URL was specified, we show an error message.
        else {
            // Get the internal document of the iframe.
            iDoc = LTI.getIframeDoc(frame[0]);

            errorMessage = '<html><head><title>Please provide LTI url.' +
                '</title></head><body><h2>Please provide LTI url. Click ' +
                '"Edit", and fill in the required fields.</h2></body>' +
                '</html>';

            // Write the error message to the iframe.
            iDoc.open();
            iDoc.write(errorMessage);
            iDoc.close();

            // Resize the ifrmae so that the error message will be seen.
            frame.width('100%').height(100);
        }
    }

    // Function getIframeDoc()
    //
    // Get the document of an iframe so that it can be written to.
    LTI.getIframeDoc = function (iframe) {
        // Create and initiate the iframe's document to null.
        var iDoc = null;

        // Depending on browser platform, get the iframe's document, this
        // is only available if the iframe has already been appended to an
        // element which has been added to the document.
        if (iframe.contentDocument) {
            // Firefox, Opera.
            iDoc = iframe.contentDocument;
        } else if (iframe.contentWindow) {
            // Internet Explorer.
            iDoc = iframe.contentWindow.document;
        } else if (iframe.document) {
            // Others?
            iDoc = iframe.document;
        }

        // If we did not succeed in finding the document then throw an
        // exception.
        if (iDoc === null) {
            throw 'Iframe document not found, append the parent element ' +
                'to the DOM before creating the IFrame';
        }

        return iDoc;
    }

    return LTI;
}());
