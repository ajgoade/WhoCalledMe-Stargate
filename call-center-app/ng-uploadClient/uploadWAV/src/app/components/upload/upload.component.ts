import {Component, OnInit} from '@angular/core';
import * as RecordRTC from 'recordRTC';
import * as  moment  from 'moment';
import {DomSanitizer} from "@angular/platform-browser";
import {UploadService} from "../../services/uploadFile/upload.service";
import {UserService} from "../../services/user/user.service";


@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent implements OnInit {


  //Lets declare Record OBJ
  record;//Will use this flag for toggling recording
  recording = false;//URL of Blob
  url;
  error;

  constructor(private domSanitizer: DomSanitizer,
              private uploadService : UploadService,
              private userService: UserService ) {
  }

  ngOnInit(): void {
  }

  sanitize(url: string) {
    return this.domSanitizer.bypassSecurityTrustUrl(url);
  }

  /**
   * Start recording.
   */
  initiateRecording() {
    this.recording = true;
    let mediaConstraints = {
      video: false,
      audio: true
    };
    navigator.mediaDevices.getUserMedia(mediaConstraints).then(this.successCallback.bind(this), this.errorCallback.bind(this));
  }

  /**
   * Will be called automatically.
   */
  successCallback(stream) {
    var options = {
      mimeType: "audio/wav",
      numberOfAudioChannels: 1,
      sampleRate: 16000,
    };//Start Actuall Recording
    var StereoAudioRecorder = RecordRTC.StereoAudioRecorder;
    this.record = new StereoAudioRecorder(stream, options);
    this.record.record();
  }

  /**
   * Stop recording.
   */
  stopRecording() {
    this.recording = false;
    this.record.stop(this.processRecording.bind(this));
  }

  /**
   * processRecording Do what ever you want with blob
   * @param  {any} blob Blog
   */
  processRecording(blob) {
    this.url = URL.createObjectURL(blob);
    console.log("blob", blob);
    console.log("url", this.url);


    this.uploadService.uploadFile(blob, this.userService.getUserName(),
      moment.now() + '-' + this.userService.getUserName() )
      .subscribe((retData) => {
          console.log('upload completed');
          console.log(retData);
        },
        (errData) => {
          console.error(errData);
          console.error('printed the error above...when tyring to POST audio file to the server');
          this.error = 'Could not send the file to the server.';
        });

  }

  /**
   * Process Error.
   */
  errorCallback(error) {
    this.error = 'Can not play audio in your browser';
  }

}
