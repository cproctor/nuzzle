
function AlarmTimer(selector, options) {
    this.init.apply(this, arguments)
}

AlarmTimer.prototype = {

    width: 180,
    height: 180,
    ringRadius: 70,
    ringStrokeWidth: 10,
    controlRadius: 12,
    TWELVE_HOURS_IN_MS: 43200000, // 12 * 60 * 60 * 1000

    init: function(element, options) {
        var self = this
        this.options = options || {}
        this.element = d3.select(element)

        if (this.options.scale) {
            this.scale(this.options.scale)
        }

        this.svg = this.element.append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .style('float', 'left')
            .on('click', function() {console.log(self)})

        this.ring = this.svg.append('circle')
                .attr('cx', this.width / 2)
                .attr('cy', this.height / 2)
                .attr('r', this.ringRadius)
                .attr('stroke-width', this.ringStrokeWidth)
                .attr('stroke', '#2C3E50')
                .attr('fill', '#ECF0F1')

        this.durationArc = this.svg.append('path')
            .attr('stroke-width', this.ringStrokeWidth)
            .attr('stroke', '#E74C3C')
            .attr('fill-opacity', 0)

        this.referenceHand = this.svg.append('line')
            .attr('x1', this.width / 2)
            .attr('y1', this.height / 2)
            .attr('stroke-width', 10)
            .attr('stroke', '#2C3E50')

        var self = this
        var dragBindings = d3.behavior.drag()
            .origin(function() {
                var controlPosition = self.timeToCoords(self.time, self.ringRadius)
                var center = {x: self.width/2, y: self.height/2}
                return {x:controlPosition.x - center.x, y:controlPosition.y - center.y}
            })
            .on("drag", function() {
                if (!self.options.disabled) {
                    self.time = self.coordsToTime(d3.event)
                    if (self.options.onChange)
                        self.options.onChange(self.time)
                    self.render()
                }
            })
            
        this.control = this.svg.append('circle')
            .attr('r', this.controlRadius)
            .attr('stroke-width', 4)
            .attr('stroke', '#E74C3C')
            .call(dragBindings)

        this.text = this.element.append('div')

        this.text.append('p')
            .attr('class', 'cp-alarm-time')
            .style('margin', 0)

        this.text.append('p')
            .attr('class', 'cp-alarm-duration')
            .style('margin', 0)

        this.element.append('div')
            .style('clear', 'both')

        this.now = moment().local()
        if (this.options.time) {
            this.time = this.options.time
        } else {
            this.time = this.now.clone().add('h', 8).add('m', 1).set('s', 0)
        }

        this.render()
        setInterval(function() {
            self.now = moment().local()
            self.render()
        }, 1000)
    },

    render: function() {

        // cast this.time to local time for the duration of the render.
        this.time.local()
        this.renderDurationArc()
        this.renderReferenceHand()
        this.renderControl()
        this.renderText()
    },

    renderDurationArc: function() {
        var start = this.timeToCoords(this.now, this.ringRadius)
        var end = this.timeToCoords(this.time, this.ringRadius)
        var elapsed = this.time.diff(this.now)
        if (elapsed >  this.TWELVE_HOURS_IN_MS / 2) 
            var largeArc = 1
        else
            var largeArc = 0
        
        pathData = ['M', start.x, start.y, 'A', this.ringRadius, 
                this.ringRadius, 0, largeArc, 1, end.x, end.y]
        this.durationArc
            .attr('d', pathData.join(' '))
    },

    renderReferenceHand: function() {
        var outerRadius = this.ringRadius + this.ringStrokeWidth / 2
        var outerRingCoords = this.timeToCoords(this.now, outerRadius)
        this.referenceHand
            .attr('x2', outerRingCoords.x)
            .attr('y2', outerRingCoords.y)
    },

    renderControl: function() {
        var self = this
        var coords = this.timeToCoords(this.time, this.ringRadius)
        this.control
            .attr('cx', coords.x)
            .attr('cy', coords.y)
            .attr('fill', function() {
                if (self.options.disabled) return '#E74C3C'
                else return '#ECF0F1'
            })
    },
    
    renderText: function() {
        var duration = moment.duration(this.time.diff(this.now))
        this.text.select('.cp-alarm-time')
            .text(this.time.format('h:mm a'))
        this.text.select('.cp-alarm-duration')
            .text(duration.humanize(true))
    },
    
    // HELPERS 

    timeToCoords: function(time, radius) {
        var radians = this.timeToRadians(time)
        var center = {x: this.width / 2, y: this.height / 2}
        return this.radiansToCoords(radians, center, radius)
    },

    coordsToTime: function(coords) {
        var radians = this.coordsToRadians(coords)
        return this.radiansToTime(radians)
    },

    radiansToCoords: function(radians, center, radius) {
        return {
            x: center.x + radius * Math.cos(radians),
            y: center.y + radius * Math.sin(radians)
        }
    },

    coordsToRadians: function(coords, center) {
        center || (center = {x:0, y:0})
        var length = Math.sqrt(
            Math.pow((coords.x - center.x), 2) + 
            Math.pow((coords.y - center.y), 2)
        )
        var nVector = {x: coords.x / length, y: coords.y / length}
        if (nVector.y < 0)
            return Math.acos(nVector.x)
        else
            return 2 * Math.PI - Math.acos(nVector.x)
    },

    timeToRadians: function(time) {
        var ms = time.diff(time.clone().startOf('day'))
        this.msToRadians = this.msToRadians || d3.scale.linear()
            .domain([0, this.TWELVE_HOURS_IN_MS])
            .range([0, 2 * Math.PI])
        return this.msToRadians(ms) - Math.PI / 2
    },

    radiansToTime: function(radians) {
        nRadians = this.normalizeRadians(radians, Math.PI / 2)
        this.radiansToMs = this.radiansToMs || d3.scale.linear()
            .domain([Math.PI / 2, 5 * Math.PI / 2])
            .range([this.TWELVE_HOURS_IN_MS, 0])
        var msToday = this.radiansToMs(nRadians)
        var newTime = this.now.clone().startOf('day')
        newTime.add('ms', msToday)
        while (newTime.diff(this.now) < 0)
            newTime.add('h', 12)
        return newTime
    },

    normalizeRadians: function(radians, offset) {
        offset || (offset = 0)
        var delta = (radians - offset) % (2 * Math.PI)
        if (delta <= 0) delta += 2 * Math.PI
        return delta + offset
    }
}

// =========================================================
var app = angular.module('nuzzleClient')

app.directive('cpAlarm', ['$parse', function($parse) {
    return {
        restrict: 'A',
        scope: {
            alarm: '=cpAlarm',
            onChange: '&cpOnChange',
            disabled: '&cpDisabled'
        },
        link: function(scope, element, attrs) {
            var options = {
                disabled: scope.disabled(),
                time: moment.utc(scope.alarm.time),
                onChange: scope.onChange()
            }
            var alarmTimer = new AlarmTimer(element[0], options)
        }
    }
}])

