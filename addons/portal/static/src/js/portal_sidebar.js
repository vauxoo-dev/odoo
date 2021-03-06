odoo.define('portal.PortalSidebar', function (require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
var Widget = require('web.Widget');
var time = require('web.time');

var _t = core._t;

var PortalSidebar = Widget.extend({
    /**
     * @override
     */
    start: function () {
        var self = this;
        this._super.apply(this, arguments);
        // Window Handlers
        $(window).on('resize', _.throttle(self._onUpdateSidebarPosition.bind(self), 200, {leading: false}));
        this._onUpdateSidebarPosition();
        this._setAffix();
        this._setDelayLabel();
    },

    //--------------------------------------------------------------------------
    // Private
    //---------------------------------------------------------------------------

    /**
     * Set the due/delay information according to the given date
     * like : <span class="o_portal_sidebar_timeago" t-att-datetime="invoice.date_due"/>
     * @private
     */
    _setDelayLabel : function () {
        var $sidebarTimeago = this.$el.find('.o_portal_sidebar_timeago');
        _.each($sidebarTimeago, function (el) {
            var dateTime = moment(time.auto_str_to_date($(el).attr('datetime'))),
                today = moment().startOf('day'),
                diff = dateTime.diff(today, 'days', true),
                displayStr;

            if (diff === 0){
                displayStr = _t('Due today');
            } else if (diff > 0) {
                displayStr = _.str.sprintf(_t('Due in %d days'), Math.abs(diff));
            } else {
                displayStr = _.str.sprintf(_t('%d days overdue'), Math.abs(diff));
            }
             $(el).text(displayStr);
        });
    },
    /**
     * updates affix status of sidebar for window scrolle
     *
     * @private
     */
    _setAffix : function () {
        var $bsSidebar = this.$el.find('.bs-sidebar');
        $bsSidebar.affix({
            offset: {
                top: 0,
                bottom: $('#wrapwrap').outerHeight() - $('main').height(),
            },
        });
    },
    /**
     * @private
     * @param {string} href
     */
    _printIframeContent: function (href) {
        // due to this issue : https://bugzilla.mozilla.org/show_bug.cgi?id=911444
        // open a new window with pdf for print in Firefox (in other system: http://printjs.crabbly.com)
        if ($.browser.mozilla) {
            window.open(href, '_blank');
            return ;
        }
        if (!this.printContent) {
            this.printContent = $('<iframe id="print_iframe_content" src="'+ href +'" style="display:none"></iframe>');
            this.$el.append(this.printContent);
            this.printContent.on('load', function () {
                $(this).get(0).contentWindow.print();
            });
        } else {
            this.printContent.get(0).contentWindow.print();
        }
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Called when the window is resized or on loadoing widget
     *
     * @private
     */
    _onUpdateSidebarPosition: function () {
        var $sidebar = this.$el.find('.bs-sidebar, .o_portal_brand');
        $sidebar.css({
            position: config.device.size_class >= config.device.SIZES.MD ? "fixed" : '',
            width: config.device.size_class >= config.device.SIZES.MD ? $sidebar.outerWidth() : '',
        });
    },
});
return PortalSidebar;
});
