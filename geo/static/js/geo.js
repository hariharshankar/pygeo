var Form;
var Search;
var Map;
var Chart;
var TypeSummary;
var CountrySummary;
var Geo;

jQuery.fn.center = function () {
    this.css("position","absolute");
    //this.css("top", Math.max(0, (($(window).height() - $(this).outerHeight()) / 2) + 
    //                                            $(window).scrollTop()) + "px");
    this.css("left", Math.max(0, (($(window).width() - $(this).outerWidth()) / 2) + 
                                                $(window).scrollLeft()) + "px");
    return this;
}

$.extend($.expr[":"], {
    "containsIn": function( elem, i, match, array) {
        return (elem.textContent || elem.innerText || "").toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
    }
});

SearchableUnits = {
    delay: function() {
        var timer = 0;
        return function( callback, ms) {
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        };
    },

    addSearch: function() {
        var form = $("<form>").attr({"class": "searchform", "action": "#"}),
            input = $("<input>").attr({
                "class": "searchinput",
                "type": "search",
                "placeholder": "Filter results by Manufacturer/Model/Type",
                "style": "font-size: 1.5em; padding: 15px; width: 500px; margin-left: 25%"
            });

        $(form).append(input).appendTo($(".search"));
        $(input).change(function() {
            var filter = $(this).val();
            if (filter.length >= 3 || filter.length == 0) {
                $(".summary-results").find(".searchable:not(:containsIn(" + filter + "))").closest(".module-container").hide();
                $(".summary-results").find(".searchable:containsIn(" + filter + ")").closest(".module-container").show();
            }
        }).keyup( function() {
            SearchableUnits.delay($(this).change(), 500);
            //$(this).change();
        });

    },

    init: function() {
        SearchableUnits.addSearch();
    }
}


Geo = {
    searchDatabase_Type_Default: "PowerPlants",
    searchType_Default: "1",
    searchCountry_Default: "99", 
    searchState_Default: "0",
    searchTab_Default: "list",

    getUserPref: function(name) {
        return $("#user_pref_"+name).val()
    },

    getPageUrl: function() {
        return window.location.href.split("?")[0]
    }
} 

AI = {
    aiDatabase_Type: "",
    aiType: "",
    aiCountry: "",
    aiState: "",
    aiTab: "",

    selectableIds: [],

    createHtmlForSelectables: function (element, data) {
        select = "";
        var k = ""
        if (data["keys"].length == 2)
            k = data['keys'][1]
        else
            k = data['keys'][0]

        if (k == "Database_Type") {
            k = "Category";
        }
        k = "Select " + k;
        var elementContentClass = element + "Content";

        var disableSelect = false
        if (Geo.getPageUrl().search("/summary/type/") >= 0 && 
                ['aiDatabase_Type', 'aiState'].indexOf(element) >= 0) {
            disableSelect = true
            if (element == "aiDatabase_Type") {
                AI[element] = "powerplants"
            }
        } 
        else if (Geo.getPageUrl().search("/summary/country/") >= 0 && 
                ['aiDatabase_Type', 'aiState', 'aiType'].indexOf(element) >= 0) {
            disableSelect = true
            if (element == "aiDatabase_Type") {
                AI[element] = "powerplants"
            }
        } 
        if (disableSelect) {
            select += "<select data-placeholder='Choose a "+k+"'class='chosen-select' style='width: 90%;' disabled='disabled'>"
        }
        else {
            select += "<select data-placeholder='Choose a "+k+"'class='chosen-select' style='width: 90%;'>"
        }
        for (var v in data['values']) {
            var value = data['values'][v]
            var v = ""
            id = 0
            if (value.length == 2) {
                id = value[0]
                v = value[1]
            }
            else {
                v = value[0]
                id = v
            }
                
            if (AI[element] == undefined) AI[element] = "";
            if (v && AI[element].toLowerCase() == v.toLowerCase() || AI[element] == id) 
                select += "<option class='ui-widget-content ui-selected "+elementContentClass+"' value='"+id+"' selected='selected'>"+v+"</option>";
            else
                select += "<option class='ui-widget-content "+elementContentClass+"' value='"+id+"'>"+v+"</option>";
        }
        select += "</select>"
        $(select).insertAfter("#"+element)
        $(".chosen-select").chosen()

        sel = $("#"+element).next()
        sel.change(function() {
            $(this).nextAll('.aiSelectableHeader').remove()
            nextSelect = $(this).next().next()
            nextSelect.nextAll('.chosen-select').remove()
            nextSelect.nextAll('.chosen-container').remove()
            AI.createSelectables(nextSelect)
        })
        heading = "<h3 class='aiSelectableHeader'>"+k+"</h3>";
        $("#"+element).before(heading)
        $("."+elementContentClass).click(function() {
            $(this).addClass("ui-selected").siblings().removeClass("ui-selected")
        })
        AI.createSelectables($("#"+element).next().next().next())
    },

    getUserValues: function() {

        params = ""
        $(".aiSelectable").each(function() {
            var key = $(this).attr("id").replace("search", "").toLowerCase()
            var value = $(this).next().next().find(".chosen-single").text()
            if ($(this).next().attr('disabled') != 'disabled') {

                if (!value || value == "") {
                    value = ""
                }
                $(this).next().children().each( function() {
                    if ($(this).text().toLowerCase() == value.toLowerCase()) {
                        params += "/" + $(this).attr('value').toLowerCase()
                    }
                });
            }
        })
        return params
    },

    getSelectValues: function (reqUrl, reqData, callbackElement) {
        $.ajax({
            type: "GET",
            url: reqUrl,
            data: reqData,
            dataType: "json",
            contentType: "application/json; charset=utf-8",            
            success: function(data, textStatus, jqXHR) {
                AI.createHtmlForSelectables(callbackElement, data)
            }
        })    
    },

    getUserValues: function() {

        params = "?"
        $(".aiSelectable").each(function() {
            var key = $(this).attr("id").replace("ai", "").toLowerCase()
            var value = $(this).next().next().find(".chosen-single").text()
            if ($(this).next().attr('disabled') != 'disabled') {

                if (!value || value == "") {
                    value = ""
                }
                $(this).next().children().each( function() {
                    if ($(this).text().toLowerCase() == value.toLowerCase()) {
                        params += key +"=" + $(this).attr('value').toLowerCase() + "&";
                    }
                });
            }
        })
        return params
    },

    createSelectables: function(t) {
        if ($(t).attr("id") == "aiUpdateButton") {
            var uservals = AI.getUserValues();
            $.ajax({url: "/get_resources" + uservals, dataType: "json",
                success: function(data, textStatus, jqXHR) {
                    var select = "<select id='selectedAI' size=12 style='min-width: 440px; height: 250px;'>"
                    for(var i=0, res; res=data.resources[i]; i++) {
                        select += "<option value='"+res.Description_ID+"' style='padding: 3px 0;'>"+res.Name_omit+"</option>";
                    }
                    select += "</select>"
                    $("#aiResources").html(select);
                }
            });

            return;
        }
        var type = $(t).attr("id").replace("ai", "")
        var url = $("#jsonListService").attr("value")
        var data = {}

        data["return_type"] = type.toLowerCase();
        if (Geo.getPageUrl().search("/new_resources/") >= 0) {
            data['new_resources'] = true;
        }

        $(t).prevAll('.aiSelectable').each( function(index) {

            var prevType = $(this).attr("id").replace("ai", "").toLowerCase()
            var prevValue = ""
             
            data[prevType] = $(this).next().next().children('.chosen-single').text()
        });
        AI.getSelectValues(url + "?" + $.param(data), null, "ai"+type)
            
        var id = $(t).attr("id")

        AI.selectableIds.push($(t).attr("id"))
    },

    showAI: function() {
        $.ajax({
            url: "/show_ai/" + $("#Description_ID").attr("value"),
            success: function(data, textStatus, jqXHR) {
                $("#AIList").empty().append(data);
            }
        });
    },

    init: function() {
        if ($("#Description_ID").attr("value") == 0) {
            $("#Associated_Infrastructure_module").html("Associated Infrastructures cannot be added for new plants at the moment.");
        }

        html = []
        html.push('<div id="AIList" class=""></div>');
        html.push("<h2>Add Associated Infrastructure by selecting a Resource below</h2><hr/><br/>");
        html.push('<div id="searchAI" class="ai-search-module">');
        html.push("<div id='aiDatabase_Type' class='aiSelectable'></div>");
        html.push("<div id='aiType' class='aiSelectable'></div>");
        html.push("<div id='aiCountry' class='aiSelectable'></div>");
        html.push("<div id='aiState' class='aiSelectable'></div>");
        html.push("<div class='aiUpdateButton' id='aiUpdateButton' style='padding-top: 10px;'>");
        html.push("<button id='createAIResource' class='createAIResource'>Add Associated Infrastructure</button>");
        html.push("</div>");

        html.push("</div>");
        html.push("<div id='aiResources' class='aiSelectable' style='top: 40px; position: relative;'>");
        html.push("</div>");

        $("#Associated_Infrastructure_module").empty().append(html.join(""));

        $("#createAIResource")
        .button()
        .click (function(event) {
            event.preventDefault()
            selectedResource = $("#selectedAI option:selected").attr("value");
            descid = $("#Description_ID").attr("value");

            if (!selectedResource) {
                return;
            }
            $.ajax({
                url: "/add_ai?did=" + descid + "&assid=" + selectedResource,
                success: function(data, textStatus, jqXHR) {
                    AI.showAI();
                }
            });

        });
        AI.createSelectables($(".aiSelectable").first());

        AI.showAI();

    }
}

Search = {

    searchDatabase_Type: "",
    searchType: "",
    searchCountry: "",
    searchState: "",
    searchTab: "",

    selectableIds: [],

    createHtmlForSelectables: function (element, data) {
        select = "";
        var k = ""
        if (data["keys"].length == 2)
            k = data['keys'][1]
        else
            k = data['keys'][0]

        if (k == "Database_Type") {
            k = "Category";
        }
        k = "Select " + k;
        var elementContentClass = element + "Content";

        var disableSelect = false
        if (Geo.getPageUrl().search("/summary/type/") >= 0 && 
                ['searchDatabase_Type', 'searchState'].indexOf(element) >= 0) {
            disableSelect = true
            if (element == "searchDatabase_Type") {
                Search[element] = "powerplants"
            }
        } 
        else if (Geo.getPageUrl().search("/summary/country/") >= 0 && 
                ['searchDatabase_Type', 'searchState', 'searchType'].indexOf(element) >= 0) {
            disableSelect = true
            if (element == "searchDatabase_Type") {
                Search[element] = "powerplants"
            }
        } 
        if (disableSelect) {
            select += "<select data-placeholder='Choose a "+k+"'class='chosen-select' style='width: 90%;' disabled='disabled'>"
        }
        else {
            select += "<select data-placeholder='Choose a "+k+"'class='chosen-select' style='width: 90%;'>"
        }
        for (var v in data['values']) {
            var value = data['values'][v]
            var v = ""
            id = 0
            if (value.length == 2) {
                id = value[0]
                v = value[1]
            }
            else {
                v = value[0]
                id = v
            }
                
            if (Search[element] == undefined) Search[element] = "";
            if (v && Search[element].toLowerCase() == v.toLowerCase() || Search[element] == id) 
                select += "<option class='ui-widget-content ui-selected "+elementContentClass+"' value='"+id+"' selected='selected'>"+v+"</option>";
            else
                select += "<option class='ui-widget-content "+elementContentClass+"' value='"+id+"'>"+v+"</option>";
        }
        select += "</select>"
        $(select).insertAfter("#"+element)
        $(".chosen-select").chosen()

        sel = $("#"+element).next()
        sel.change(function() {
            $(this).nextAll('.searchSelectableHeader').remove()
            nextSelect = $(this).next().next()
            nextSelect.nextAll('.chosen-select').remove()
            nextSelect.nextAll('.chosen-container').remove()
            Search.createSelectables(nextSelect)
        })
        heading = "<h3 class='ui-widget-header module-header searchSelectableHeader'>"+k+"</h3>";
        $("#"+element).before(heading)
        $("."+elementContentClass).click(function() {
            $(this).addClass("ui-selected").siblings().removeClass("ui-selected")
        })
        Search.createSelectables($("#"+element).next().next().next())
    },

    getUserValues: function() {

        params = ""
        $(".searchSelectable").each(function() {
            var key = $(this).attr("id").replace("search", "").toLowerCase()
            var value = $(this).next().next().find(".chosen-single").text()
            if ($(this).next().attr('disabled') != 'disabled') {

                if (!value || value == "") {
                    value = ""
                }
                $(this).next().children().each( function() {
                    if ($(this).text().toLowerCase() == value.toLowerCase()) {
                        params += "/" + $(this).attr('value').toLowerCase()
                    }
                });
            }
        })
        return params
    },

    getSelectValues: function (reqUrl, reqData, callbackElement) {
        $.ajax({
            type: "GET",
            url: reqUrl,
            data: reqData,
            dataType: "json",
            contentType: "application/json; charset=utf-8",            
            success: function(data, textStatus, jqXHR) {
                Search.createHtmlForSelectables(callbackElement, data)
            }
        })    
    },

    createSelectables: function(t) {
        if ($(t).attr("id") == "searchUpdateButton") {
            return;
        }
        var type = $(t).attr("id").replace("search", "")
        var url = $("#jsonListService").attr("value")
        var data = {}

        data["return_type"] = type.toLowerCase();
        if (Geo.getPageUrl().search("/new_resources/") >= 0) {
            data['new_resources'] = true;
        }

        $(t).prevAll('.searchSelectable').each( function(index) {

            var prevType = $(this).attr("id").replace("search", "").toLowerCase()
            var prevValue = ""
             
            data[prevType] = $(this).next().next().children('.chosen-single').text()
        });
        Search.getSelectValues(url + "?" + $.param(data), null, "search"+type)
            
        var id = $(t).attr("id")

        Search.selectableIds.push($(t).attr("id"))
    },
    
    plantListPostData: {},

    init: function() {
        var shdReloadPage = false
        var params = {}
        params['database_type'] = Geo.getUserPref("db_type")
        params['type'] = Geo.getUserPref("type")
        params['country'] = Geo.getUserPref("country")
        params['state'] = Geo.getUserPref("state")

        Search.searchDatabase_Type = params['database_type']
        Search.searchType = params['type']
        Search.searchCountry = params['country']
        Search.searchState = params['state']
        Search.searchTab = params['tab']    

        
        Search.createSelectables($(".searchSelectable").first())

        $("#createResource")
        .button()
        .click (function(event) {
            event.preventDefault()
            params = Search.getUserValues()
            base_url = Geo.getPageUrl()
            
            b = base_url.replace("http://", "").split('/')
            url = "http://" + b[0] + "/";

            url += "new_resources";
            if (['type', 'country'].indexOf(b[2]) >= 0) {
                url += "/" + b[2];
            }
            window.location.href = url + params
        });

        $("#updateSearch")
        .button()
        .click (function(event) {
            event.preventDefault()
            params = Search.getUserValues()
            base_url = Geo.getPageUrl()
            
            b = base_url.replace("http://", "").split('/')
            url = "http://" + b[0] + "/";

            if (['resources', 'summary', 'map', 'analyze', 'allunits'].indexOf(b[1]) >= 0) {
                url += b[1];
                if (['type', 'country'].indexOf(b[2]) >= 0) {
                    url += "/" + b[2];
                }
            }
            else {
                url += "resources"
            }
            window.location.href = url + params
        })

        $(".leftPane-header").click( function(event) {
            var panel = $(this).next();
            var isOpen = panel.is(":visible");

            panel[isOpen? 'slideUp': 'slideDown']()
            .trigger(isOpen? 'hide': 'show');

            if (isOpen) {
                $($(this).children()[0]).switchClass("ui-icon-circle-minus", "ui-icon-circle-plus");
                $(this).addClass("ui-corner-bottom");
                $(this).addClass("ui-accordion-header")
            }
            else {
                $($(this).children()[0]).switchClass("ui-icon-circle-plus", "ui-icon-circle-minus");
                $(this).removeClass("ui-corner-bottom");
                $(this).removeClass("ui-accordion-header")
            }

            return false;
        });
    }
}


Form = {
    createSingleRowButtons: function() {
        var button = '';
        button += "<button class='add-single-row-button'>Add another row</button>";
        button += "</span><span>";
        button += "<button class='remove-single-row-button'>Delete selected row</button>";
        return button;
    },

    initPerformance: function() {

        $("#Annual_Performance").prepend("<button id='plot_performance_parmeters'>Plot selected parameters vs years</button>");
        $("#Annual_Performance").prepend("<button id='plot_performance_ratio'>Plot ratio of 2 selected parameters</button>");
        $("#Annual_Performance").prepend("<div id='performance_chart' style='width: 650px; height: 400px; overflow: hidden;'></div>")
        $("#performance_chart").dialog({
            height: 420,
            width: 700,
            modal: true,
            autoOpen: false,
            close: function(event, ui) {
                $("#performance_chart").empty();
                $("#performance_chart").css("width", "650")
                $("#performance_chart").css("height", "400")
            }
        });
        
        $("#plot_performance_ratio").button()
            .click( function(event) {
                event.preventDefault();
                data = {}
                data['keys'] = []
                data['values'] = []
                data['keys'].push('Year')
                checkedFields = []
                keyText = "Ratio of "
                $(".performance-label input").each( function() {
                    if (this.checked) {
                        checkedFields.push(this)
                        var id = $(this).attr("id").split('_###_')[0];
                        keyText += id + " ";
                    }
                });
                data['keys'].push(keyText);
                if (checkedFields.length != 2) {
                    return;
                }
                for (var year=1950; year<2020; year++) {
                    d = []
                    for (f in checkedFields) {
                        var id = $(checkedFields[f]).attr("id").split('_###_')[0];
                        id = id.replace(/[^\w\*\s]/g, "\\$&")

                        id += "_\\#\\#\\#_";
                        v = $("#" + id + year).val();
                        if (v.trim() != "") {
                            if (d.length == 0) {
                                d.push(year);
                            }
                            d.push(v);
                        }
                    }
                    if (d.length > 0 && d[1] != 0 && d[2] != 0) {
                        data['values'].push([d[0], d[1]/d[2]]);
                    }
                }
                if (data['values'].length > 0) {
                    d = Chart.parseChartData(data);

                    Chart.plotLineChart(d, "performance_chart");
                    $("#performance_chart").dialog("open");
                }
            });

        $("#plot_performance_parmeters").button()
            .click( function(event) {
                event.preventDefault();
                data = {}
                data['keys'] = []
                data['values'] = []
                data['keys'].push('Year')
                checkedFields = []
                $(".performance-label input").each( function() {
                    if (this.checked) {
                        checkedFields.push(this)
                        var id = $(this).attr("id").split('_###_')[0];
                        data['keys'].push(id)
                    }
                });
                for (var year=1950; year<2020; year++) {
                    d = []
                    for (f in checkedFields) {
                        var id = $(checkedFields[f]).attr("id").split('_###_')[0];
                        id = id.replace(/[^\w\*\s]/g, "\\$&")

                        id += "_\\#\\#\\#_";
                        v = $("#" + id + year).val();
                        if (v.trim() != "") {
                            if (d.length == 0) {
                                d.push(year);
                            }
                            d.push(v);
                        }
                    }
                    if (d.length > 0) {
                        data['values'].push(d);
                    }
                }
                if (data['values'].length > 0) {
                    d = Chart.parseChartData(data);

                    Chart.plotLineChart(d, "performance_chart");
                    $("#performance_chart").dialog("open");
                }
            });


        // adjust performance value/label height to be in sync
        //$(".performance-label").offset({top: $(".performance-values").offset().top})
        /*$(".performance-values").width($("#Annual_Performance").width() 
                                            - $(".performance-label").width()
                                           - 20); 
        */
        $(".performance-values").width($("#Annual_Performance_module").width() 
                                            - $(".performance-label").width()
                                            - 20); 
        // setting the scrollbar to point to 2010
        // TODO: try to calculate this dynamically
        $(".performance-values").scrollLeft(2868);
    },

    addNuclearPerformanceUnit: function() {
        var numberOfUnits = +$("#numberOfNuclear_Unit_Description").val() - 1;
        var vals = $($(".performance-values .odd-row")[0]).html();
        vals = vals.replace(/value="[a-z0-9.]*"/g, "value=''");
        $(".performance-label .perf-row").each( function(rowIndex, v) {
            if ($(this).text() == "Gigawatt Hours Generated " + numberOfUnits 
                || $(this).text() == "Capacity Generated " + numberOfUnits) {
                var ele = $(this).html();
                ele = ele.split(numberOfUnits).join(numberOfUnits+1);

                $(ele).insertAfter(this);
                vals = vals.split("_" + numberOfUnits + "_").join("_" + numberOfUnits+1 + "_");
                $(vals).insertAfter($(".performance-values").children()[rowIndex]);
            }
        });
        


    },
    addSingleRow: function(ele) {
        $(ele).parent().children().each( function() {
            if ($(this)[0].tagName.toLowerCase() == "table") {
                var parentTable = $(this); 
                var newRow = $(parentTable).find(".single-rows").last().html();
                newRow = "<tr>" + newRow + "</tr>";

                var index = 0;
                $(parentTable).children().first().children().each( function() {
                    if ($(this).attr && $(this).attr("type") == "hidden") {
                        index = parseInt($(this).attr("value")) + 1;
                        $(this).attr("value", index.toString());
                    }
                });
                var n = "";
                for (var i=0, c; c=$(newRow).children()[i]; i++) {
                    if ($(c).children().length > 0) {
                        var t = $(c).children().first();
                        $(t).attr("value", "");
                        if ($(t).attr("name")) {
                            var elementName = $(t).attr("name").split("_###_")[0] + "_###_" + index;
                            $(t).attr("name", elementName);
                            $(t).attr("id", elementName);
                            n += "<td>" + $(t)[0].outerHTML + "</td>";
                        }
                    }
                    else if (i == 1) {
                        n += "<td>" + index + "</td>";
                    }
                }

                $("<tr class='single-rows'>"+n+"</tr>").insertAfter($(parentTable).find(".single-rows").last());
            }
        });
        if ($("#Type_ID").val() == "5") {
            Form.addNuclearPerformanceUnit();
        }
    },
    removeSingleRow: function(ele) {
                $(ele).parent().parent().find(".single-rows").each( function() {
                    if ($(this).children().first().children().first()[0].checked) {
                        $(this).parent().parent().children().first().children().each( function() {
                            if ($(this).attr && $(this).attr("type") == "hidden") {
                                var v = parseInt($(this).attr("value")) - 1;
                                $(this).attr("value", v.toString());
                            }
                        });
                        $(this).remove();
                    }
                });
                var i =0;
                $(ele).parent().parent().find(".single-rows").each( function() {
                    i++;
                    var k=0;
                    $(this).children().each( function() {
                        k++;
                        var el = $(this).children().first();
                        var id = el.attr("id");
                        if (id && id.search("_###_") > 0) {
                            el.attr("id", id.split("_###_")[0] + "_###_" + i);
                            el.attr("name", id.split("_###_")[0] + "_###_" + i);
                        }
                        else if (k == 2) {
                            el.context.innerHTML = i;
                        }
                    });
                });
            },

    createAbstract: function() {
        var abstract = "";
        abstract += $("#Name_omit").val();
        abstract += " is located at ";
        abstract += $("#Location").val();
        abstract += ". It's location coordinates are: ";
        abstract += "Latitude = " + $("#Latitude_Start").val() + ", Longitude = " + $("#Longitude_Start").val() + ". ";
        abstract += "This infrastructure is of TYPE " + $("#Type_Name").val();
        abstract += " with a design capacity of " + " MWe. ";
        abstract += "It is operated by " + $("#Operating_Company").val() + ".";

        $("#Abstract_module").text(abstract);
    },

    init: function() {

        $("#submit").button().center();
        $("#moderate").center();

        $("#accept_moderate").button()
        .click(function(event) {
            event.preventDefault();
            window.location.href = "/moderationsubmit/?geoid="+$("#Description_ID").val()+"&moderation=1&moderation_comment=" + $("#comments_moderate").val()
        });
        $("#reject_moderate").button()
        .click(function(event) {
            event.preventDefault();
            window.location.href = "/moderationsubmit/?geoid="+$("#Description_ID").val()+"&moderation=0&moderation_comment=" + $("#comments_moderate").val()
        });

        $(".module-header").click( function(event) {
            var panel = $(this).next();
            var isOpen = panel.is(":visible");

            panel[isOpen? 'slideUp': 'slideDown']()
            .trigger(isOpen? 'hide': 'show');

            if (isOpen) {
                $($(this).children()[0]).switchClass("ui-icon-circle-minus", "ui-icon-circle-plus");
                $(this).removeClass("ui-widget-header");
                $(this).addClass("ui-corner-bottom");
                $(this).addClass("ui-accordion-header")
                $(this).addClass("ui-state-default")
            }
            else {
                $($(this).children()[0]).switchClass("ui-icon-circle-plus", "ui-icon-circle-minus");
                $(this).addClass("ui-widget-header");
                $(this).removeClass("ui-corner-bottom");
                $(this).removeClass("ui-accordion-header")
                $(this).removeClass("ui-state-default")
            }

            return false;
        });

        $(".single-row-module").each( function() {
            $(this).next().append(Form.createSingleRowButtons());
        });

        $(".add-single-row-button")
            .button()
            .click(function(event) {
                event.preventDefault();
                Form.addSingleRow(this);
            });


        $(".remove-single-row-button")
            .button()
            .click(function(event) {
                event.preventDefault();
                Form.removeSingleRow(this);
            });
        Form.initPerformance();
        AI.init()
        Map.init(true);
    }
}


Chart = {
    plotLineDataTable: function(lineData, tableContainer) {

        var years = lineData[0]['xvalues']
        var w = $("#"+tableContainer).width()-20;

        var html = ''
        html += "<table style='width: "+w+"; height: 400px;' class='line-html-table'>";
        html += "<tr class='line-html-table-header'>";
        html += "<th class='ui-widget-header'>Year</th>";
        for (var k in lineData) {
            html += "<th class='ui-widget-header'>"+lineData[k]['ylabel']+"</th>";
        }
        html += "</tr>";

        var count = 0;
        
        for (var y in years) {
            html += "<tr>";
            html += "<td class='line-html-table-years'>"+years[y]+"</td>";

            for (k in lineData) {
                data = lineData[k]['yvalues']
                html += "<td align='center'>"+data[y]+"</td>";
            }
            html += "</tr>";
            count++;
        }
        
        html += "</table>";
        $("#"+tableContainer).append(html)
    },

    plotBubbleChart: function(bubbleData, chartContainer) {
        var values = []
        for (var k in bubbleData) {
            values.push({"size": bubbleData[k], "name": k})
        }
        var json = {
            "name": "type",
            "children": values
        };

        var r = 500,
        format = d3.format(",d"),
        fill = d3.scale.category20c();

        var bubble = d3.layout.pack()
        .sort(null)
        .size([r, r])
        .padding(1.5);

        var vis = d3.select("#"+chartContainer).append("svg")
        .attr("width", r)
        .attr("height", r)
        .attr("class", "bubble");


        var node = vis.selectAll("g.node")
        .data(bubble.nodes(classes(json))
        .filter(function(d) { return !d.children; }))
        .enter().append("g")
        .attr("class", "node")
        .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

        node.append("title")
        .text(function(d) { return d.className + ": " + format(d.value); });

        node.append("circle")
        .attr("r", function(d) { return d.r; })
        .style("fill", function(d) { return fill(d.packageName); });

        node.append("text")
        .attr("text-anchor", "middle")
        .attr("dy", ".3em")
        .text(function(d) { return d.className.substring(0, d.r / 3); });

        // Returns a flattened hierarchy containing all leaf nodes under the root.
        function classes(root) {
            var classes = [];

            function recurse(name, node) {
                if (node.children) node.children.forEach(function(child) { recurse(node.name, child); });
                else classes.push({packageName: name, className: node.name, value: node.size});
            }

            recurse(null, root);
            return {children: classes};
        }
    },

    showData: function(obj, d) {
        var coord = d3.mouse(obj);
        var infobox = d3.select(".chart_infobox");
        // now we just position the infobox roughly where our mouse is
        infobox.style("left", (coord[0] + 100) + "px" );
        infobox.style("top", (coord[1] - 100) + "px");
        $(".chart_infobox").html(d);
        $(".chart_infobox").show();
    },
 
    hideData: function() {
        $(".chart_infobox").hide();
    },

    plotLineChart: function(lineData, chartContainer) {

        // define dimensions of graph
        var m = [80, 85, 80, 80]; // margins
        var w = $("#"+chartContainer).width() - m[1] - m[3]; // width
        var h = $("#"+chartContainer).height() - m[0] - m[2]; // height

        $("#"+chartContainer).append("<div class='chart_infobox' style='display:none;'>Value</div>");

        // Add an SVG element with the desired dimensions and margin.
        var graph = d3.select("#"+chartContainer).append("svg:svg")
                    .attr("width", w + m[1] + m[3])
                    .attr("height", h + m[0] + m[2])
                    .append("svg:g")
                    .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

        var colors = ["crimson", "steelblue", "forestgreen", "mediumvioletred", "black"] 

        // X scale will fit all values from data[] within pixels 0-w
        var startYear = lineData[0].xvalues[0];
        var yearLen = lineData[0].xvalues.length;
        var endYear = lineData[0].xvalues[yearLen-1];
        var x = d3.time.scale().domain([new Date((startYear).toString()), new Date((endYear).toString())]).range([0,w]);

        // create xAxis
        var xAxis = d3.svg.axis().orient("bottom").scale(x);

        // Add the x-axis.
        graph.append("svg:g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + h + ")")
            .call(xAxis)
            .append("text")
            .attr("x", w/2 - 30)
            .attr("y", 40)
            .attr("dx", ".71em")
            .style("fill", "black")
            .text("Year");

        // create a line function that can convert data[] into x and y points
        var line = d3.svg.line()
                    .interpolate('monotone')
                    // assign the X function to plot our line as we wish
                    .x(function(d,i) { 
                        return x(new Date(lineData[0].xvalues[i].toString()));
                    })
                    .y(function(d) { 
                        return y(d); 
                    })

        var y;
        for (var lineCount=0; lineCount<lineData.length; lineCount++) {
            y = d3.scale.linear().domain([0, d3.max(lineData[lineCount].yvalues)]).range([h, 0]);

            // left side y axis
            if (lineCount == 0) {
                // create left yAxis
                var yAxisLeft = d3.svg.axis().scale(y).ticks(6).orient("left");
                // Add the y-axis to the left
                graph.append("svg:g")
                    .attr("class", "y axis axisLeft")
                    .attr("transform", "translate(-15,0)")
                    .style("fill", colors[lineCount])
                    .call(yAxisLeft)
                    .append("text")
                    .attr("transform", "rotate(-90)")
                    .attr("y", 6)
                    .attr("dy", ".71em")
                    .style("fill", colors[lineCount])
                    .style("text-anchor", "end")
                    .text(lineData[lineCount].ylabel);
            }
            // second, right side y axis
            else {
                // create right yAxis
                var yAxisRight = d3.svg.axis().scale(y).ticks(6).orient("right");
                // Add the y-axis to the right
                graph.append("svg:g")
                    .attr("class", "y axis axisRight")
                    .attr("transform", "translate(" + (w+15) + ",0)")
                    .style("fill", colors[lineCount])
                    .call(yAxisRight)
                    .append("text")
                    .attr("transform", "rotate(-90)")
                    .attr("y", -12)
                    .attr("dy", ".71em")
                    .style("text-anchor", "end")
                    .style("fill", colors[lineCount])
                    .text(lineData[lineCount].ylabel);
            }
        var series = graph.append('svg:g')
                        .data([lineData[lineCount]])
                        .attr("class", "series");

        // add lines
        series.append("svg:path")
            .attr("d", function(d, i) {return line(d.yvalues)})
            .attr("class", "linepath")
            .style("stroke", function(d, i) { return colors[lineCount]})
            .style("stroke-width", "4px")
        series.selectAll(".point")
                        //.data(data[lineCount])
                        .data(function (d, i) { return d.yvalues; })
                        .enter().append("circle")
                        .attr("class", "point")
                        .attr("fill", "black")
                        .attr("cx", function(d, i) { return x(new Date(lineData[0].xvalues[i].toString())); })
                        .attr("cy", function(d, i) { return y(d); })
                        .attr("r", 5)
                        .on("mouseover", function(d) { Chart.showData(this, d);})
                        .on("mouseout", function(){ Chart.hideData();});

        }
    },


    parseChartData: function(d) {
        values = []
        for (k=1; k<d.keys.length; k++) {
            var years = []
            var dLine = [];
            var value = {}
            value['xlabel'] = d.keys[0];
            for (v=0; v<d.values.length; v++) {
                if (years.indexOf(d.values[v][0]) < 0) {
                    years.push(d.values[v][0]);
                }
                if (!d.values[v][k]) {
                    val = null;
                }
                else {
                    val = d.values[v][k];
                }
                dLine.push(Math.round(val * 100) / 100);
            }
            key = d.keys[k].replace("_nbr", "")
            value['ylabel'] = key
            value['xvalues'] = years
            value['yvalues'] = dLine
            values.push(value)
        }
        return values
    },

    getPerformanceCumulativeChart: function() {

        var years = []
        var keys = []
        var data = []

        $.getJSON($("#performance_linechart_cumulative_json_url").attr("value"), function(d) {
            var arr = Chart.parseChartData(d)
            keys = arr[0]
            years = arr[1]
            data = arr[2]
        })
        .done( function() { 
            var lineData = { "years": years, "data": data, "keys": keys };
            Chart.plotLineChart(lineData, "performance_linechart_cumulative_chart")
            Chart.plotLineDataTable(lineData, "performance_linechart_cumulative_table")
        })
        .fail( function() { return null; } );
    },

    getUnitCumulativeCapacityChart: function() {

        var years = []
        var keys = []
        var data = []

        $.getJSON($("#unit_linechart_cumulative_json_url").attr("value"), function(d) {
            var arr = Chart.parseChartData(d)
            keys = arr[0]
            years = arr[1]
            data = arr[2]
        })
        .done( function() { 
            var lineData = { "years": years, "data": data, "keys": keys };
            Chart.plotLineChart(lineData, "unit_linechart_cumulative_chart")
            Chart.plotLineDataTable(lineData, "unit_linechart_cumulative_table")
        })
        .fail( function() { return null; } );
    },
    
    plotPieChart: function(data, container_id) {

        traditional = ['coal', 'oil', 'gas', 'nuclear', 'waste'];
        renewable = ['geothermal', 'solar_pv', 'solar_thermal', 'wind', 'hydro'];

        traditional_data = {}
        traditional_data['values'] = []
        traditional_data['labels'] = []
        renewable_data = {}
        renewable_data['values'] = []
        renewable_data['labels'] = []
        $(".pie_chart_values").each(function(i, v) {
            if (traditional.indexOf(v.id.toLowerCase()) >= 0) {
                traditional_data['values'].push(+v.value);
                traditional_data['labels'].push(v.id);
            }
            else if (renewable.indexOf(v.id.toLowerCase()) >= 0) {
                renewable_data['values'].push(+v.value);
                renewable_data['labels'].push(v.id);
            }
        });

        for (i=1; i<=2; i++) {
            var container = container_id + "_" + i;
            width = $("#" + container).width();
            height = $("#" + container).height();
            radius = Math.min(width, height) / 2;

            var color = d3.scale.category20();

            var pie = d3.layout.pie()
                .sort(null);

            var pie_data;
            if (i == 1) {
                pie_data = traditional_data;
            }
            else if (i == 2) {
                pie_data = renewable_data;
            }
            var piedata = pie(pie_data.values);

            var arc = d3.svg.arc()
                .innerRadius(radius - 100)
                .outerRadius(radius - 50);

            var svg = d3.select("#" + container).append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

            var path = svg.selectAll("path")
                .data(piedata)
                .enter().append("path")
                .attr("fill", function(d, i) { return color(i); })
                .attr("class", "donut")
                .attr("d", arc);

            svg.selectAll("text").data(piedata)
                .enter()
                .append("text")
                .attr("text-anchor", "middle")
                .attr("x", function(d) {
                    var a = d.startAngle + (d.endAngle - d.startAngle)/2 - Math.PI/2;
                    d.cx = Math.cos(a) * (radius - 75);
                    return d.x = Math.cos(a) * (radius - 20);
                })
            .attr("y", function(d) {
                var a = d.startAngle + (d.endAngle - d.startAngle)/2 - Math.PI/2;
                d.cy = Math.sin(a) * (radius - 75);
                return d.y = Math.sin(a) * (radius - 20);
            });
            /*
            .text(function(d, i) { return pie_data.labels[i] + " - " + d.value + " MWe"; })
                .each(function(d) {
                    var bbox = this.getBBox();
                    d.sx = d.x - bbox.width/2 - 2;
                    d.ox = d.x + bbox.width/2 + 2;
                    d.sy = d.oy = d.y + 5;
                });
                */
var legendRectSize = (radius * 0.05);
var legendSpacing = radius * 0.02;

//console.log(pie_data);
var pie_perc = [];
var sum=0;
for (var k=0, f; f=pie_data.values[k]; k++) {
    sum += f;
}
for (var k=0, f; f=pie_data.values[k]; k++) {
    pie_perc[k] = (f/sum) * 100;
}
var legend = svg.selectAll('.legend')
        .data(color.domain())
        .enter()
        .append('g')
        .attr('class', 'legend')
        .attr('transform', function(d, i) {
            var height = legendRectSize + legendSpacing;
            var offset =  height * color.domain().length / 2;
            var horz = -3 * legendRectSize;
            var vert = i * height - offset;
            return 'translate(' + horz + ',' + vert + ')';
        });

    legend.append('rect')
        .attr('width', legendRectSize)
        .attr('height', legendRectSize)
        .style('fill', color)
        .style('stroke', color);

    legend.append('text')
        .attr('x', legendRectSize + legendSpacing)
        .attr('y', legendRectSize - (legendSpacing-4))
        .text(function(d) { return pie_data.labels[d] + ", " + parseFloat(pie_perc[d]).toFixed(2) + "%"; });

/*
            svg.append("defs").append("marker")
                .attr("id", "circ")
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("refX", 3)
                .attr("refY", 3)
                .append("circle")
                .attr("cx", 3)
                .attr("cy", 3)
                .attr("r", 3);

            svg.selectAll("path.pointer").data(piedata).enter()
                .append("path")
                .attr("class", "pointer")
                .style("fill", "none")
                .style("stroke", "black")
                .attr("marker-end", "url(#circ)")
                .attr("d", function(d) {
                    if(d.cx > d.ox) {
                        return "M" + d.sx + "," + d.sy + "L" + d.ox + "," + d.oy + " " + d.cx + "," + d.cy;
                    } else {
                        return "M" + d.ox + "," + d.oy + "L" + d.sx + "," + d.sy + " " + d.cx + "," + d.cy;
                    }
                });
                */
        }
    }

    /*
    plotPieChart: function(data, container) {
        width = $("#" + container).width();
        height = $("#" + container).height();
        radius = Math.min(width, height) / 2;

        var color = d3.scale.ordinal()
                    .range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);

        var arc = d3.svg.arc()
                    .outerRadius(radius - 10)
                    .innerRadius(0);

        var pie = d3.layout.pie()
                    .sort(null)
                    .value(function(d) { return d.values; });

        //var pie = function(d) { console.log(d); }

        var svg = d3.select("#" + container).append('svg')
                    .attr("width", width)
                    .attr("height", height)
                    .append("g")
                    .attr("transform", "translate(" + width/2 + "," + height/2 + ")");

        pie_data = []

        $(".pie_chart_values").each(function(i, v) {
            pie_data.push({'labels': v.id, 'values': +v.value})
        });

        console.log(pie_data)
        piedata = pie(pie_data)
    
        var g = svg.selectAll(".arc")
                .data(piedata)
                .enter().append("g")
                .attr("class", "arc");

        g.append("path")
            .attr("d", arc)
            .style("fill", function(d, i) { return color(i % 7); });

        //
        g.append("text")
            .attr("transform", function(d, i) { return "translate(" + arc.centroid(d) + i + ")"; })
            .attr("dy", ".35em")
            .style("text-anchor", "middle")
            .text(function(d) { return d.data.labels; });
        //
svg.selectAll("text").data(piedata)
    .enter()
    .append("text")
    .attr("text-anchor", "middle")
    .attr("x", function(d) {
        var a = d.startAngle + (d.endAngle - d.startAngle)/2 - Math.PI/2;
        d.cx = Math.cos(a) * (radius - 75);
        return d.x = Math.cos(a) * (radius - 20);
    })
    .attr("y", function(d) {
        var a = d.startAngle + (d.endAngle - d.startAngle)/2 - Math.PI/2;
        d.cy = Math.sin(a) * (radius - 75);
        return d.y = Math.sin(a) * (radius - 20);
    })
    .text(function(d) { return d.labels; })
    .each(function(d) {
        var bbox = this.getBBox();
        d.sx = d.x - bbox.width/2 - 2;
        d.ox = d.x + bbox.width/2 + 2;
        d.sy = d.oy = d.y + 5;
    });

svg.append("defs").append("marker")
    .attr("id", "circ")
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("refX", 3)
    .attr("refY", 3)
    .append("circle")
    .attr("cx", 3)
    .attr("cy", 3)
    .attr("r", 3);


svg.selectAll("path.pointer").data(piedata).enter()
    .append("path")
    .attr("class", "pointer")
    .style("fill", "none")
    .style("stroke", "black")
    .attr("marker-end", "url(#circ)")
    .attr("d", function(d) {
        //console.log(d)
        if(d.cx > d.ox) {
            x = "M" + d.sx + "," + d.sy + "L" + d.ox + "," + d.oy + " " + d.cx + "," + d.cy;
            console.log(x)
            return x
        } else {
            return "M" + d.ox + "," + d.oy + "L" + d.sx + "," + d.sy + " " + d.cx + "," + d.cy;
        }
    });
    }
    */
}

Map = {
    bounds: null,
    map: null,
    geoCodeLatLng: null,
    mapColors: ["#FF0000", "#0008FF", "#187F00", "#9F9C00", "#FAA701", "#01DDD9"],
    overlaysCount: 0,
    mapOpacity: 0.4,
    mapStrokeWeight: 1,
    overlaysArray: [],
    savedMarker: null,

    addOverlayDetails: function(overlayType, overlayArea, overlayLength, overlayNumber, points, overlayName) {
        var type_name = $("#Type_Name").val()
        var overlayColor = Map.mapColors[overlayNumber-1]
        var details = "";
        overlayNumber = parseInt(overlayNumber)
        if (overlayName == "null") {
            overlayName = "";
        }
        if (overlayNumber > Map.overlaysCount) {
            details += "<div id='overlay_"+overlayNumber+"' name='overlay_"+overlayNumber+"' >";
            details += "<span id='overlay_color_"+overlayNumber+"' name='overlay_color_"+overlayNumber+"' style='background: "+overlayColor+"; width: 10px; height: 10px;'>&nbsp;&nbsp;&nbsp;</span>&nbsp;"
            if (overlayType == "Polygon") {
                details += "<span id='overlay_area_"+overlayNumber+"'>Area: <b>"+overlayArea+" km<sup>2</sup></b>&nbsp;|&nbsp;</span>"
            }
            else if (overlayType == "Polyline") {
                details += "<span id='overlay_area_"+overlayNumber+"'>Length: <b>"+parseFloat(overlayLength/1000).toFixed(2)+" km</b>&nbsp;|&nbsp;</span>"
            }
            if (document.getElementById("Overlay_Name_###_"+overlayNumber) != "" && overlayName ) {
                details += "<span>Description: <input type='input' size='15' id='Overlay_Name_###_"+overlayNumber+"' name='Overlay_Name_###_"+overlayNumber+"' value='"+overlayName+"' /></span>";
            }
            else {
                details += "<span>Description: <input type='input' size='15' id='Overlay_Name_###_"+overlayNumber+"' name='Overlay_Name_###_"+overlayNumber+"' /></span>";
            }
            details += "</div>";
            details += this.createHiddenHtmlElement("Color_###_"+overlayNumber, overlayColor)
            details += this.createHiddenHtmlElement("Points_###_"+overlayNumber, points)
            details += this.createHiddenHtmlElement("Overlay_Type_###_"+overlayNumber, overlayType)
            overlayCounter = Map.overlaysCount + 1
            if (!document.getElementById("numberOf"+type_name+"_Overlays")) {
                details += this.createHiddenHtmlElement("numberOf"+type_name+"_Overlays", overlayCounter)
            }
            else {
                $("#numberOf"+type_name+"_Overlays").attr("value", overlayCounter)
            }

            $("#overlay-details").append(details);
        }
        else {
            $("#overlay_area_"+overlayNumber).html("Area : <b>"+overlayArea+" km<sup>2</sup></b>&nbsp;|&nbsp;");
            document.getElementById("Points_###_"+overlayNumber).setAttribute("value", points)
        }

    },

    updateOverlayData: function(overlay, overlayType, overlayNumber, overlayName) {
        var overlayPoints = overlay.getPath().getArray()
        var points = ""
        for (var i=0,p; p=overlayPoints[i]; i++) {
            points += "[" + p.lat() + "," + p.lng() + "],"
        }
        // removing the trailing comma
        points = points.substr(0, points.length-1)

        points = "[" + points + "]"
        
        overlayArea = Math.round(google.maps.geometry.spherical.computeArea(overlay.getPath()) / 10000) / 100
        overlayLength = google.maps.geometry.spherical.computeLength(overlay.getPath())

        Map.addOverlayDetails(overlayType, overlayArea, overlayLength, overlayNumber, points, overlayName)
    },

    addOverlayEvents: function(overlay, overlayType, overlayNumber) {
        google.maps.event.addListener(overlay, "mouseover", function() {
            overlay.setEditable(true)
        })
        google.maps.event.addListener(overlay, "mouseout", function() {
            overlay.setEditable(false)
        })
        google.maps.event.addListener(overlay.getPath(), "insert_at", function() {
            Map.updateOverlayData(overlay, overlayType, overlayNumber, "")
        })
        google.maps.event.addListener(overlay.getPath(), "set_at", function() {
            Map.updateOverlayData(overlay, overlayType, overlayNumber, "")
        })
    },

    getDrawingTools: function(count) {
        var drawingManager = new google.maps.drawing.DrawingManager({
                drawingControl: true,
                drawingControlOptions: {
                    position: google.maps.ControlPosition.TOP_CENTER,
                    drawingModes: [
                        google.maps.drawing.OverlayType.POLYGON,
                        google.maps.drawing.OverlayType.POLYLINE
                    ]
                }
        });

        var overlayType;
        var overlayArea;
        var overlayLength;

        google.maps.event.addListener(drawingManager, "overlaycomplete", function(event) {
            var options = {
                fillColor: Map.mapColors[Map.overlaysCount],
                fillOpacity: Map.mapOpacity,
                strokeWeight: Map.mapStrokeWeight,
                clickable: false,
                zIndex: 1,
                editable: true,
                draggable: true
            }
            event.overlay.setOptions({'options': options})
            overlayType = drawingManager.getDrawingMode()
            overlayType = overlayType[0].toUpperCase() + overlayType.substr(1, overlayType.length)
        
            Map.addOverlayEvents(event.overlay, overlayType, Map.overlaysCount+1)
            Map.updateOverlayData(event.overlay, overlayType, Map.overlaysCount+1, "")

            Map.overlaysCount++
        })
        return drawingManager;
    },

    getMapBounds: function(point, status) {
        if( point && point.length > 0 ) {
            Map.bounds = point[0].geometry.viewport
            Map.geoCodeLatLng = point[0].geometry.location
            if (Map.bounds) {
                Map.map.fitBounds(Map.bounds)
            }
        }
    },

    createHiddenHtmlElement: function(name, value) {
        return '<input type="hidden" name="'+name+'" id="'+name+'" value="'+value+'" />';
    },

    drawSavedOverlays: function(overlays) {
        var overlayHtml = []
        for (var o in overlays) {
            var overlay = overlays[o]
            var pointsString = overlay.points

            //console.log(pointsString)
            var points = eval(pointsString)
            var pointsArray = []
            
            for (var p=0; p<points.length; p++) {
                pointsArray.push(new google.maps.LatLng(points[p][0], points[p][1]))
            }
            if (overlay.overlayType == "Polygon") {
                Map.overlaysArray[Map.overlaysCount] = new google.maps.Polygon({
                    path: pointsArray,
                    fillColor: overlays[o].color,
                    fillOpacity: Map.mapOpacity,
                    strokeWeight: Map.mapStrokeWeight,
                    map: Map.map
                });
            }
            else {
                Map.overlaysArray[Map.overlaysCount] = new google.maps.Polyline({
                    path: pointsArray,
                    strokeColor: overlays[o].color,
                    strokeOpacity: 1.0,
                    strokeWeight: 3,
                    map: Map.map
                });
            }
            var overlayNumber = parseInt(o) + 1
            Map.addOverlayEvents(Map.overlaysArray[Map.overlaysCount], overlays[o].overlayType, overlayNumber)
            Map.updateOverlayData(Map.overlaysArray[Map.overlaysCount], overlays[o].overlayType, overlayNumber, overlays[o].overlayName)
            Map.overlaysCount++;
        }
    },

    showLatLng: function(lat, lng) {
        var html = ""
        html += "<b>Latitude:</b>&nbsp;<input type='text' size='10' name='Latitude_Start' id='Latitude_Start' value='"+lat+"' />&nbsp;"
        html += "<b>Longitude:</b>&nbsp;<input type='text' size='10' name='Longitude_Start' id='Longitude_Start' value='"+lng+"' />&nbsp;"
        html += "<button id='restore_placemarks' name='restore_placemarks'>Restore Placemarks</button>";

        html += "<br/>"

        html += this.createHiddenHtmlElement("Latitude_Start_old", lat);
        html += this.createHiddenHtmlElement("Longitude_Start_old", lng);

        $("#overlay-details").prepend(html)
        Form.createAbstract();
        $("#restore_placemarks")
        .button()
        .click( function(event) {
            event.preventDefault();
            var old_lat = $("#Latitude_Start_old").val();
            var old_lng = $("#Longitude_Start_old").val();
            $("#Latitude_Start").val(old_lat);
            $("#Longitude_Start").val(old_lng);
            //latlng = new google.maps.LatLng({lat: parseInt(old_lat), lng: parseInt(old_lng)});
            Map.savedMarker.setPosition({lat: parseFloat(old_lat), lng: parseFloat(old_lng)});
        });

    },

    plotOverlays: function(data, showDrawingTools) {

            data = data.data
            var searchLocation = data.boundLocation;

            var geoCodeSearch = false;
            if (searchLocation != null || searchLocation != "") {
                var geoCoder = new google.maps.Geocoder();
                geoCodeSearch = true;
                geoCoder.geocode({'address': searchLocation, 'partialmatch':true}, Map.getMapBounds);
            }
            $("#map-container").width("100%")
            $("#map-container").height("600px")

            Map.map = new google.maps.Map(document.getElementById('map-container'), {
                zoom: 15,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            });

            $("#map-resize").resizable({
                maxWidth: $("#map-resize").width(),
                minWidth: $("#map-resize").width(),
                maxHeight: 900,
                minHeight: $("#map-resize").height() + 15,
                stop: function(e, ui) {
                    $("#map-container").height( $("#map-resize").height() );
                    google.maps.event.trigger(Map.map, 'resize');
                }
            });

            // adding drawing tools
            if (showDrawingTools) {
                Map.getDrawingTools().setMap(Map.map)
            }

            var marker;
            if (!data.locations && geoCodeSearch) {
                setTimeout(function() {
                    lat = Map.geoCodeLatLng.lat()
                    lng = Map.geoCodeLatLng.lng()

                    Map.showLatLng(lat, lng)
                    marker = new google.maps.Marker({
                        position: new google.maps.LatLng(lat,lng),
                        map: Map.map
                    });
                }, 1000);

                return;
            }
            $.each(data.locations, function(location) {
                var lat,lng,name;
                if (data.locations[location][0] != undefined) {
                    lat = data.locations[location][0];
                    lng = data.locations[location][1];
                    name = data.locations[location][2];
                }
                else {
                    lat = data.locations[location]['lat'];
                    lng = data.locations[location]['lng'];

                    var lat_end = null;
                    var lng_end = null;
                    if (data.locations[location]['lat_end'] != undefined) {
                        lat_end = data.locations[location]['lat_end'];
                        lng_end = data.locations[location]['lng_end'];
                    }

                    // drawing saved overlays
                    name = data.locations[location]['name'];
                    if (data.locations[location]['overlays'] != null) {
                        if (data.locations[location]['overlays'].length > 0) {
                            var overlays = data.locations[location]['overlays'];
                            Map.drawSavedOverlays(overlays);
                        }
                    }
                }

                // adjusting the map bounds for a single location map
                // TODO: set zoom level
                if (searchLocation == null || searchLocation == "") {
                    Map.showLatLng(lat, lng)
                    geoCoder.geocode({'location': new google.maps.LatLng(lat, lng)}, Map.getMapBounds)
                }
                marker = new google.maps.Marker({
                    position: new google.maps.LatLng(lat,lng),
                    editable: true,
                    draggable: true,
                    map: Map.map
                });

                google.maps.event.addListener(marker, 'dragend', (function(marker, location) {
                    return function() {
                        $("#Latitude_Start").val(marker.position.lat());
                        $("#Longitude_Start").val(marker.position.lng());
                    }
                })(marker, location));
                google.maps.event.addListener(marker, 'click', (function(marker, location) {
                    return function() {
                        var infoWindow = new google.maps.InfoWindow();
                        infoWindow.setContent(name);
                        infoWindow.open(Map.map, marker)
                    }
                })(marker, location));

                Map.savedMarker = marker;

                if (lat_end != null) {
                    Map.showLatLng(lat_end, lng_end)
                    marker_end = new google.maps.Marker({
                        position: new google.maps.LatLng(lat_end,lng_end),
                        editable: true,
                        draggable: true,
                        map: Map.map
                    });
                    google.maps.event.addListener(marker_end, 'click', (function(marker_end, location) {
                        return function() {
                            var infoWindow = new google.maps.InfoWindow();
                            infoWindow.setContent(name);
                            infoWindow.open(Map.map, marker_end)
                        }
                    })(marker_end, location));
                }
            });
        
        },

    init: function(showDrawingTools) {

        if( document.getElementById('map-container') == undefined ) {
            return;
        }
        $.getJSON($("#map_json").attr("value"), function(data) {
            Map.plotOverlays(data, showDrawingTools);
        });
        $.getJSON($("#ai_map_json").attr("value"), function(data) {
            //Map.plotOverlays(data, false, true);
            data = data.data.locations[0]
                    lat = data['lat']
                    lng = data['lng']

                    // drawing saved overlays
                    name = data['name']
                    if (data['overlays'] != null) {
                        if (data['overlays'].length > 0) {
                            var overlays = data['overlays']
                            Map.drawSavedOverlays(overlays)
                        }
                    }
        });
    }
}

CountrySummary = {
    init: function() {
        Chart.plotPieChart('', 'pie_chart');
    }
},

TypeSummary = {

    displayTypeSummaryResults: function(numberOfPlants, cumulativeCapacityTotal, tableContainer) {

        var w = $("#"+tableContainer).width();

        var html = ''
        html += "<table style='width: 50%; height: 100%; overflow: auto; margin: auto;' class='line-html-table'>";
        html += "<tr>";
        html += "<td class='line-html-table-years'>Total Number of Plants: </td>";
        html += "<td align='right'><b>"+numberOfPlants+"</b></td>";
        html += "</tr>";
        
        html += "<tr>";
        html += "<td class='line-html-table-years'>Total Cumulative Capacity (MWe): </td>";
        html += "<td align='right'><b>"+cumulativeCapacityTotal+"</b></td>";
        html += "</tr>";
        html += "<tr style='height: 10px;' />";
        html += "<tr/>";

        /*
        html += "<tr>";
        html += "<td colspan='2' class='line-html-table-years' style='font-weight: bold; font-size: 1.2em;'>Cumulative Capacity by Type (in MWe)</td>";
        html += "</tr>";

        var url = $("#summary_json").attr("value")
        url = url.replace(new RegExp(".type_id=[0-9]{1,2}"), "")
        $.getJSON(url, function(d) {
            d = d.data
            cumulativeCapacity = {}
            numberOfPlants = {}
            for (j=0,k=""; k=d.keys[j]; j++) {
                if (k.search("Cumulative_Capacity") == 0) {
                    for (i=0; i<d.values.length; i++) {
                        var type = ""
                        for (t=0; t<Summary.typeValues.values.length; t++) {
                            if (Summary.typeValues.values[t][0] == d.values[i][0]) {
                                type = Summary.typeValues.values[t][1]
                                break
                            }
                        }
                        cumulativeCapacity[type] = d.values[i][j]
                        
                        html += "<tr>";
                        html += "<td class='line-html-table-years'>"+type+": </td>";
                        html += "<td align='right'>"+d.values[i][j]+"</td>";
                        html += "</tr>";
        
                    }
                }
                else if (k.search("Number_of_Plants") == 0) {
                    for (i=0; i<d.values.length; i++) {
                        numberOfPlants[d.values[i][0]] = d.values[i][j]
                    }
                }
            }
            html += "</table>";
            $("#"+tableContainer).append(html)
        })
        */
        html += "</table>";
        $("#"+tableContainer).append(html)
    },

    typeValues: {},

    init: function() {

        var reqUrl = $("#jsonListService").attr("value")
        var reqData = {}
        reqData["return_type"] = "Type"
        reqData["Database_Type"] = ["powerplants"]
        $.ajax({
            type: "GET",
            url: reqUrl,
            data: $.param(reqData),
            dataType: "json",
            contentType: "application/json; charset=utf-8",            
            success: function(data, textStatus, jqXHR) {
                TypeSummary.typeValues = data
            }
        })    


        $.getJSON($("#summary_json").attr("value"), function(d) {
            var numberOfPlants = 0
            var cumulativeCapacityTotal = 0
            var newCapAddedIndex = 0
            var cumulativeCapAddedIndex = 0
            var annGWhGenIndex = 0
            var annCO2EmIndex = 0

            //d = d.data
            for (var i=0, k; k=d.keys[i]; i++) {
                if (k.search("New_Capacity_Added") == 0) {
                    newCapAddedIndex = i
                }
                else if (k.search("Annual_Gigawatt_Hours_Generated") == 0) {
                    annGWhGenIndex = i
                }
                else if (k.search("Annual_CO2_Emitted") == 0) {
                    annCO2EmIndex = i
                }
                else if (k.search("Cumulative_Capacity_Total") == 0) {
                    cumulativeCapacityTotal = d.values[i]
                }
                else if (k.search("Cumulative_Capacity") == 0) {
                    cumulativeCapAddedIndex = i
                }
                else if (k.search("Number_of_Plants") == 0) {
                    numberOfPlants = d.values[i]
                }
            }

            TypeSummary.displayTypeSummaryResults(numberOfPlants, cumulativeCapacityTotal, "summary-overview")

            newCapArr = Chart.parseChartData(d.values[newCapAddedIndex])
            newCapKeys = newCapArr[0]
            newCapYears = newCapArr[1]
            newCapData = newCapArr[2]

            cumCapArr = Chart.parseChartData(d.values[cumulativeCapAddedIndex])
            cumCapKeys = cumCapArr[0]
            cumCapYears = cumCapArr[1]
            cumCapData = cumCapArr[2]

            var perfCumulativeChartData = []
            var perfCumulativeChartKeys = []

            var annCO2Em = d.values[annCO2EmIndex]
            var annGWhGen = d.values[annGWhGenIndex]
            perfCumulativeChartKeys = annGWhGen.keys
            perfCumulativeChartKeys.push(annCO2Em.keys[1])

            for (v in annGWhGen.values) {
                perfCumulativeChartData.push([annGWhGen.values[v][0], annGWhGen.values[v][1], annCO2Em.values[v][1]])
            }

            arr = Chart.parseChartData({"keys": perfCumulativeChartKeys, "values": perfCumulativeChartData})
            cumKeys = arr[0]
            cumYears = arr[1]
            cumData = arr[2]
        }) 
        .done( function() { 
            var lineData = { "years": cumYears, "data": cumData, "keys": cumKeys };
            Chart.plotLineChart(arr, "performance_linechart_cumulative_chart")
            Chart.plotLineDataTable(arr, "performance_linechart_cumulative_table")
            
            lineData = { "years": newCapYears, "data": newCapData, "keys": newCapKeys };
            Chart.plotLineChart(newCapArr, "unit_linechart_capacity_chart")
            Chart.plotLineDataTable(newCapArr, "unit_linechart_capacity_table")

            lineData = { "years": cumCapYears, "data": cumCapData, "keys": cumCapKeys };
            Chart.plotLineChart(cumCapArr, "unit_linechart_cumulative_chart")
        })
        .fail( function() { return null; } );
    }
}
