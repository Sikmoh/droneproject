
//setInterval(api, 5000)

async function api(){


    let url = "http://192.168.247.223:5003/telemetry";
    const response = await fetch(url);
    //var telemetry = await response.json();

    //console.log(telemetry)
    let d = new Date();
      document.getElementById("clock").innerHTML=
      d.getHours() + ":" +
      d.getMinutes() + ":" +
      d.getSeconds();
//    window.location = window.location.href;

}


    //console.log('removed')




setInterval(api, 2000)