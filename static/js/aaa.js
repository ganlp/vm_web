define("aurora/components/notification-item",["exports","aurora/app"],function(e,t){
	Object.defineProperty(e,"__esModule",{value:!0})
	e.default=t.default.NotificationItemComponent=Ember.Component.extend({
		HIDE_DELAY:4e3,
		isHiding:!1,
		tagName:"li",
		classNames:["item"],
		classNameBindings:["typeClass"],
		typeClass:function(){
			return this.get("item.type")}.property("item.type"),
			startHideTimer:function(e){
				this.hideTimeout=window.setTimeout(Ember.run.bind(this,this.hide),this.HIDE_DELAY/(e?2:1))
				},
			show:function(){
				Ember.run.next(Ember.run.bind(this,function(){this.$().addClass("show"),this.startHideTimer()}))
				}.on("didInsertElement"),
			hide:function(){
				var e=this.$()
				e&&e.removeClass("show").one(
					"transitionend webkitTransitionEnd",Ember.run.bind(this,function(){e.off("transitionend webkitTransitionEnd"),
					t.default.NotificationsManager.remove(this.get("item"))})),
				this.isHiding=!0
				},
			mouseEnter:function(){
				window.clearTimeout(this.hideTimeout)},
			mouseLeave:function(){
				this.isHiding||this.startHideTimer(!0)},
			click:function(){
				this.hide(),window.clearTimeout(this.hideTimeout)}
	})}),




define("aurora/components/notification-list",["exports","aurora/app"],function(e,t){
	Object.defineProperty(e,"__esModule",{value:!0}),
	t.default.NotificationsManager=Ember.Object.create({
		notifications:Ember.A(),
		pendingRemovals:[],
		show:function(e,t,n){
			var a={message:e||"",type:t||"",link:n}
			return this.notifications.pushObject(a),a},
		remove:function(e){
			this.pendingRemovals.push(e),this.pendingRemovals.length===this.notifications.length&&(this.pendingRemovals.forEach(function(e){this.notifications.removeObject(e)}.bind(this)),this.pendingRemovals=[])}
	}),
	t.default.NotificationListComponent=Ember.Component.extend({
		classNames:["aurora-notifications"],
		tagName:"ul",
		notifications:t.default.NotificationsManager.get("notifications"),
		setup:function(){
			if("undefined"==typeof ReactRailsUJS){var e=Ember.$(".flash-holder"),n=void 0,a=void 0
				e.each(function(e,s){n=Ember.$(s).data("message"),a=Ember.$(s).data("type"),t.default.NotificationsManager.show(n,a)})}
		}.on("didInsertElement")}),e.default=t.default.NotificationListComponent
}),





define("aurora/components/notifications-nav-count",["exports"],function(e){
	Object.defineProperty(e,"__esModule",{value:!0})
	e.default=Ember.Component.extend({
		tagName:"span",
		classNames:["notification-count"],
		displayCount:function(){
			var e=this.get("pendingNotificationsCount")
			return e>99&&(e="+99"),e}.property("pendingNotificationsCount")

			})}),

/*
-----------------------------------------------------------------------------------------------------------------


define("aurora/components/notification-item",["exports","aurora/app"],function(e,t){
	Object.defineProperty(e,"__esModule",{value:!0})
	e.default=t.default.NotificationItemComponent=Ember.Component.extend({
		HIDE_DELAY:4e3,
		isHiding:!1,
		tagName:"li",
		classNames:["item"],
		classNameBindings:["typeClass"],
		typeClass:function(){
			return this.get("item.type")
			}.property("item.type"),
		startHideTimer:function(e){
			this.hideTimeout=window.setTimeout(Ember.run.bind(this,this.hide),this.HIDE_DELAY/(e?2:1))},
		show:function(){
			Ember.run.next(Ember.run.bind(this,function(){this.$().addClass("show"),this.startHideTimer()}))
			}.on("didInsertElement"),
		hide:function(){var e=this.$()
			e&&e.removeClass("show").one("transitionend webkitTransitionEnd",Ember.run.bind(this,function(){
				e.off("transitionend webkitTransitionEnd"),t.default.NotificationsManager.remove(this.get("item"))})),
			this.isHiding=!0},
		mouseEnter:function(){
			window.clearTimeout(this.hideTimeout)},
		mouseLeave:function(){
			this.isHiding||this.startHideTimer(!0)},
		click:function(){
			this.hide(),window.clearTimeout(this.hideTimeout)}
	})}),


define("aurora/components/notification-list",["exports","aurora/app"],function(e,t){
	Object.defineProperty(e,"__esModule",{value:!0}),
	t.default.NotificationsManager=Ember.Object.create({
		notifications:Ember.A(),
		pendingRemovals:[],
		show:function(e,t,n){
			var a={message:e||"",type:t||"",link:n}
			return this.notifications.pushObject(a),a},
		remove:function(e){
			this.pendingRemovals.push(e),
			this.pendingRemovals.length===this.notifications.length&&(this.pendingRemovals.forEach(function(e){
				this.notifications.removeObject(e)
				}.bind(this)),this.pendingRemovals=[])}}),
	t.default.NotificationListComponent=Ember.Component.extend({
		classNames:["aurora-notifications"],
		tagName:"ul",
		notifications:t.default.NotificationsManager.get("notifications"),
		setup:function(){
			if("undefined"==typeof ReactRailsUJS){
				var e=Ember.$(".flash-holder"),
				n=void 0,
				a=void 0
				e.each(function(e,s){
					n=Ember.$(s).data("message"),
					a=Ember.$(s).data("type"),
					t.default.NotificationsManager.show(n,a)})}
			}.on("didInsertElement")}),
	e.default=t.default.NotificationListComponent}),


define("aurora/components/notifications-nav-count",["exports"],function(e){
	Object.defineProperty(e,"__esModule",{value:!0})
	e.default=Ember.Component.extend({
		tagName:"span",
		classNames:["notification-count"],
		displayCount:function(){
			var e=this.get("pendingNotificationsCount")
			return e>99&&(e="+99"),e
			}.property("pendingNotificationsCount")})}),
--------------------------------------------------------------------

t.default.NotificationsManager.show("Sorry, we only support PNGs, JPGs and GIFs.","alert")
t.default.NotificationsManager.show(n.error.message,"alert")
t.default.NotificationsManager.show(n,"alert")
t.default.NotificationsManager.show("Sorry! We were unable to initialize the billing client.","alert")
n.default.NotificationsManager.show("Your certificate has been added.","notice")
t.default.NotificationsManager.show(e.get("successMessage"),"notice")

e.createUserResponse(t),e.sendAction("onProjectGoalsSubmit",n)}).catch(function(){e.sendAction("transitionToDashboard")})}).catch(function(){
var t=s.default.NotificationsManager.show("Something went wrong.","alert")
setTimeout(function(){
		return s.default.NotificationsManager.remove(t),e.sendAction("transitionToDashboard")},
2e3)}
)},

*/