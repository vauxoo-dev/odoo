define([
  'summernote/EventHandler',
], function (Editor) {

  Editor.prototype.getLinkInfo = function ($editable) {
      // ODOO MODIFICATION START
      var selection;
      var currentSelection = null;
      if (document.getSelection) {
        selection = document.getSelection();
        if (selection.getRangeAt && selection.rangeCount) {
          currentSelection = selection.getRangeAt(0);
        }
      }
      // ODOO MODIFICATION END

      this.focus($editable);

      // ODOO MODIFICATION START
      if (currentSelection && document.getSelection) {
        selection = document.getSelection();
        selection.removeAllRanges();
        selection.addRange(currentSelection);
      }
      // ODOO MODIFICATION END

      var rng = range.create().expand(dom.isAnchor);

      // Get the first anchor on range(for edit).
      var anchor = list.head(rng.nodes(dom.isAnchor));
      const $anchor = $(anchor);

      if ($anchor.length && !rng.nodes()[0].isSameNode(anchor)) {
        rng = range.createFromNode(anchor);
        rng.select();
      }

      // Check if the target is a button element.
      let isButton = false;
      if (!$anchor.length) {
        const pred = dom.makePredByNodeName('BUTTON');
        const rngNew = range.create().expand(pred);
        const target = list.head(rngNew.nodes(pred));
        if (target && target.nodeName === 'BUTTON') {
          isButton = true;
          rng = rngNew;
        }
      }

      return {
        range: rng,
        text: rng.toString(),
        isNewWindow: $anchor.length ? $anchor.attr('target') === '_blank' : false,
        url: $anchor.length ? $anchor.attr('href') : '',
        isButton: isButton,
      };
    };
});
