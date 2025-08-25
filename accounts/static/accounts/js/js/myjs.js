$(document).ready(
function($) {
var endpoint="/jsonData/";
var labels=[]
var data=[]
var colors=[]
$.ajax({
type:"GET",
url:endpoint,
success:function(res){
	console.log(res.labels)
	console.log(res.sales)
labels=res.labels
data=res.sales
colors=res.colors

var ctx = $("#myChart")
var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels:labels ,
        datasets: [{
            label: '# of Votes',
            data: data,
            backgroundColor:colors,
            borderColor: colors,
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero:true
                }
            }]
        }
    }
});
}

})

})



$(document).ready(function($) {
  console.log('trending')

var display=function(){
var endpoint_trending="/Api/Headlines/trending";
var labels=[]
var data=[]
var colors=[]
$.ajax({
type:"GET",
url:endpoint_trending,
success:function(res){
 
labels=res.titles
data=res.likes
colors=res.colors

var ctx = $("#myChart-trending")
var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels:labels ,
        datasets: [{
            label: 'Trending news',
            data: data,
            backgroundColor:colors,
            borderColor: colors,
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero:true
                }
            }]
        }
    }
});
}

})
}

display()
window.setInterval(display, 200000);
    
});