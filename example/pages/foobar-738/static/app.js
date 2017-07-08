var app = {};
app.selector = "section.graphic";
app.el = $(app.selector);

app.boot = function () {
    var filler = $("<div>")
      .css("font-size", "50px")
      .css("color", "#ffffff")
      .css("text-align", "center")
      .css("line-height", "600px")
      .css("background-color", "#e6e6e6")
      .html("THIS IS NOT A GRAPHIC");
    filler = $("<div>")
      .css("margin-top", "30px")
      .css("margin-bottom", "30px")
      .css("height", "600px")
      .append(filler);
    this.el.append(filler);
};
