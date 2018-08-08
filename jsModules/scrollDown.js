return new Promise(resolve => {
    var offset = -100;
    let pageScroll = () => {
        window.scrollBy(0, 50);
        if (window.pageYOffset === offset) {
            return resolve(true);
        }
        offset = window.pageYOffset;
        setTimeout(pageScroll, 50);
    };
    pageScroll();

}).then((val) => {
    window.alert(val);
});
