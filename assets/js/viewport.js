/* Tarayıcı boyutunu viewport-store'a yazar.
 * Dash ClientsideFunction(namespace='viewport', function_name='updateViewport')
 * ile çağrılır.
 */
if (!window.dash_clientside) { window.dash_clientside = {}; }

window.dash_clientside.viewport = {
    updateViewport: function (dummy) {
        return {
            width:  window.innerWidth  || document.documentElement.clientWidth  || document.body.clientWidth,
            height: window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight
        };
    }
};
