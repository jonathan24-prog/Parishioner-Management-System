
$(document).ready(function($) {




  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});



$('#form_upload').submit(function(event) {
  event.preventDefault()
  console.log('upload')
  var thisURL = $(this).attr('data-href') || window.location.href
  var formData = $(this).serialize()
  
  $.ajax({
    method: "POST",
    url: thisURL,
    data: formData,

    success:function(data){
      console.log(data)
    },
    error: function(e){
      console.log(e)
    }

    

    
  })

  
});





currentRow = null;
var is_updated=null

$('#subject-body').on('click','#delete-subject-loaded',function(e){

    var $thisURL = $(this).attr('data-href') || window.location.href 
    var tr=$(this).closest('tr')
    $.ajax({

        method:"POST",
        url:$thisURL,
        success: function(data){

          if(data.is_delete == true){

             tr.fadeOut('1000', function() {
            $(this).remove();    
            });

          }
           
        },
        error: function(e){

        }

    })
})

$('#subject-body').on('click','#drop-subject-loaded',function(e){
    console.log('ni abot diri')
    currentRow= $(this).parents('tr');

    var $thisURL = $(this).attr('data-href') || window.location.href 
    console.log($thisURL)
    var tr=$(this).closest('tr')
    $.ajax({

        method:"POST",
        url:$thisURL,
        success: function(data){

          if(data.is_drop == true){

                  $("#subject-body").find($(currentRow)).replaceWith(`<tr id="subject-tr" data-id="${data.pk}">
                  <td class="code"data-id="${data.subject_pk}">${data.code}</td>
                  <td class="description">${data.description}</td>
                  <td class="unit">${data.unit}</td>
                  <td class="status">${data.status}</td>


            <td><a data-href="/Api/${data.pk}/enroll/subjects/drop/" class="btn btn-sm btn-danger" id="drop-subject-loaded">Drop</a>
            </td>
  
                  </tr>`);
         }

          
           
        },
        error: function(e){

        }

    })
})


$('#subject-body').on('click','#edit-subject-loaded',function(e){
    currentRow= $(this).parents('tr');
    console.log($(this).parents('tr').attr('data-id'))
    $('#is_updated').val($(this).parents('tr').attr('data-id'));
    $("#id_subject").val($(this).closest('tr').find('td.subject').attr('data-id'));

is_updated=$(this).parents('tr').attr('data-id')
$('.collapse').collapse('show')

$('#save-subject').text('Update')
})

$('#btn-enroll').click(function(e){
  console.log('hahaha')
var $url= $(this).attr('data-href') || window.location.href
$.ajax({
    url: $url,
    type: 'POST',
    success:function(data){
        if(data.message=="ok"){
           $('#p-status').text('Status:'+data.enroll_status)
           $("#subject-body").children("tr").remove();
            for(i in data.subjects){
           $('#subject-body').append(`<tr id="subject-tr" data-id="${data.subjects[i].pk}">
            <td class="subject" data-id="${data.subjects[i].subject_pk}">${data.subjects[i].code}</td>
            <td>${data.subjects[i].description}</td>
            <td>${data.subjects[i].unit}</td>
            <td>${data.subjects[i].status}</td>
            <td><a data-href="/Api/${data.subjects[i].pk}/enroll/subjects/drop/" id="delete-subject-loaded" class="btn btn-sm btn-warning">drop</a>
            </td>    
            </tr>`)

         }
 
        }

    },
    error: function(e){
        console.log(e)
    }
})

})

$('#btn-return').click(function(e){
  console.log('hahaha')
var $url= $(this).attr('data-href') || window.location.href
$.ajax({
    url: $url,
    type: 'POST',
    success:function(data){
        if(data.message=="ok"){
           $('#p-status').text('Status:'+data.enroll_status)
           $("#subject-body").children("tr").remove();
            for(i in data.subjects){
           $('#subject-body').append(`<tr id="subject-tr" data-id="${data.subjects[i].pk}">
            <td class="subject" data-id="${data.subjects[i].subject_pk}">${data.subjects[i].code}</td>
            <td>${data.subjects[i].description}</td>
            <td>${data.subjects[i].unit}</td>
            <td>${data.subjects[i].status}</td>
            <td><a data-href="/Api/${data.subjects[i].pk}/enroll/subjects/drop/" id="delete-subject-loaded" class="btn btn-sm btn-warning disabled muted">drop</a>
            </td>    
            </tr>`)

         }
 
        }

    },
    error: function(e){
        console.log(e)
    }
})

})


$('#Subject-add').click(function(){
       $('.collapse').collapse('show')



})


var $formSubject = $('#form-addSubject');
$formSubject.submit(function(event){
    event.preventDefault()
       console.log('ni abot')
        
 console.log(is_updated)

     var $thisURL = $formSubject.attr('data-href-add') || window.location.href 
   
        console.log($thisURL)// or set your own url
         var $formData = $(this).serialize()

        $.ajax({
            method: "POST",
            url: $thisURL,
            data: $formData,
            success: function(data){
              console.log(data)
              if(data.is_save){
                console.log('ni abot diri')



              $('#subject-body').append(`<tr id="subject-tr" data-id="${data.pk}">
                  <td class="subject" data-id="${data.subject_pk}">${data.code}</td>
                  <td>${data.description}</td>
                  <td>${data.unit}</td>
                  <td>${data.status}</td>

                  <td><a data-href="/Api/${data.pk}/enroll/subjects/delete/" id="delete-subject-loaded" class="btn btn-sm btn-warning">delete</a>
                                 </td>
                  </tr>`)

              // $('.collapse').collapse('hide')

              $('#id_subject').val('')
             


              


              
              }

              else{

                alert(data.message)
              }
              

              // if(data.is_updated){

              //    $("#subject-body").find($(currentRow)).replaceWith(`<tr id="subject-tr" data-id="${data.pk}">
              //     <td class="code"data-id="${data.subject_pk}">${data.code}}</td>
              //     <td class="description">${data.description}</td>
              //     <td class="unit">${data.unit}</td>
              //     <td class="status">${data.status}</td>

              //                       <td><a data-href="/Api/${data.pk}/enroll/subjects/delete/" id="delete-subject-loaded"><i class="fa fa-close text-danger"></i></a>
            
              //     </td>
              //     </tr>`);

              //    // $('.collapse').collapse('hide')
              //       $('#id_subject').val('')


           
              // }

        
          },
          error: handleFormError,
      })
    });


function handleFormSuccess(data, textStatus, jqXHR){


    alert(data.message)
    if(data.is_save){
      $('#btn-enroll').addClass('disabled')
      $('#btn-enroll').addClass('muted')

  }

}
function handleFormError(jqXHR, textStatus, errorThrown){
    console.log(jqXHR)
    console.log(textStatus)
    console.log(errorThrown)
}













})
