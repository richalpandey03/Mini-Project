const express = require("express");
const bodyParser = require("body-parser");
const multer = require("multer");
const path = require("path");
const { spawn } = require("child_process");
const res = require("express/lib/response");
//const ejs=require("ejs");

const app = express();

app.set('view engine', 'ejs');

app.use(bodyParser.urlencoded({
  extended: true
}));


app.use(express.static("public"));

const storage = multer.diskStorage({
    destination : (req, file,cb) => {
        cb(null,'car')
    },
    filename : (req, file, cb) => {
        console.log(file);
        cb(null,file.fieldname+""+path.extname(file.originalname));
    }
})
const upload = multer({storage : storage});

const storage1 = multer.diskStorage({
    destination : (req, file,cb) => {
        cb(null,'qrimg')
    },
    filename : (req, file, cb) => {
        console.log(file);
        cb(null,file.fieldname+""+path.extname(file.originalname));
    }
})
const upload1 = multer({storage : storage1});


app.get("/",function(req,res){
    res.sendFile(__dirname+"/public/index.html");
})

app.post("/plate", upload.single("car"),(req,res) => {
    
    res.sendFile(__dirname+"/public/lic.html");
})

app.post("/qrcode", upload1.single("qr"),(req,res) => {
  
    res.sendFile(__dirname+"/public/qrcode.html");
   
})

app.post("/detect",validate);

function validate(req,res){
    const childPython = spawn('python',['anpr.py']);
childPython.stdout.on('data',(data) =>{
    console.log(data.toString());
    console.log(data.length);
        // res.send(data.toString());
        res.render("final",{plateNumber : data.toString().slice(0,45),
        qrvalue: data.toString().slice(45,56),
        compare : data.toString().slice(56)

        });
   

    })

}

app.listen(3000,function() {
    console.log("started");
});