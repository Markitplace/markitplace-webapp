/// <reference path="../../../typings/jquery/jquery.d.ts"/>
function initialize(pages) {
	var mapOptions = {
          center: new google.maps.LatLng(pages.lat, pages.lon),
          zoom: 17,
		  streetViewControl: false
        }
    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
	setMarkers(map, pages);
	
	function setMarkers(map, locations) {
  		var image = 'static/img/markitmarker.png'
  
  
    //var locaion = locations;
    	var myLatLng = new google.maps.LatLng(pages.lat, pages.lon);
    	var marker = new google.maps.Marker({
        	position: myLatLng,
        	map: map,
        	icon: image,
        	title: pages.name
    
  			});

  	google.maps.event.addListener(marker, 'click', toggleBounce);
	}
  }
  


	function toggleBounce() {

  		if (marker.getAnimation() != null) {
    		marker.setAnimation(null);
  		} else {
   			marker.setAnimation(google.maps.Animation.BOUNCE);
			marker.setAnimation(null);
  		}
	}
      //google.maps.event.addDomListener(window, 'load', initialize);
  
$(document).ready(function(){
	$(document.body).on('click', '.editPost', function(e){
		var postID = $(this).attr('id');
		$('#post-body').val($('#post'+postID).text());
		$("#editPostModal").modal();
		$(function() {
    $('#save-post-edit').click(function(){
		$.post('/postEdit', { 
			id: postID, 
			body: $('#post-body').val()
		}, function() {
			$('#editPostModal').modal('hide');
			location.reload(true);
		}).fail(
			//$('#post-edit-error').show()
		);
    });
});
	});
	


});

