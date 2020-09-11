import {Component, OnInit} from '@angular/core';
import * as RecordRTC from 'recordRTC';
import * as  moment  from 'moment';
import {DomSanitizer} from "@angular/platform-browser";
import {UploadService} from "../../services/uploadFile/upload.service";
import {UserService} from "../../services/user/user.service";
import {GetTranscriptionService} from "../../services/getTranscription/get-transcription.service";


@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent implements OnInit {

  speech = {
    id: 0,
    transcription: '',
    sentiment: '',
    localFileUrl: '',
    status: 'none',
    remoteUrl : '',
    timeUpdated: ''
  };

  showTranscription = false;
  pollingHandler=null;
  //Lets declare Record OBJ
  record;//Will use this flag for toggling recording
  recording = false;//URL of Blob
  url;
  error;

  constructor(private domSanitizer: DomSanitizer,
              private uploadService : UploadService,
              private userService: UserService,
              private getTranscriptionService: GetTranscriptionService) {
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
    this.showTranscription = false;
    if (this.pollingHandler) {
      clearTimeout(this.pollingHandler);
    };

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
    let options = {
      mimeType: "audio/wav",
      numberOfAudioChannels: 1,
      desiredSampRate: 16000,
    };//Start Actual Recording
    let StereoAudioRecorder = RecordRTC.StereoAudioRecorder;
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

    this.showTranscription = true;
    this.speech = {
      id: 0,
      transcription: '',
      sentiment: '',
      status: 'Prep to upload',
      localFileUrl: this.url,
      timeUpdated: '',
      remoteUrl: ''
    };


    this.url = URL.createObjectURL(blob);
    console.log("blob", blob);
    console.log("url", this.url);


    this.speech = {
      id: 0,
      transcription: '',
      sentiment: '',
      status: 'Uploading file...',
      localFileUrl: '',
      remoteUrl: '',
      timeUpdated: ''
    };


    this.uploadService.uploadFile(blob, this.userService.getUserName(),
      moment.now() + '-' + this.userService.getUserName() + '.wav')
      .subscribe((retData) => {
          console.log('upload completed');
          console.log(retData);

          let id = retData['id'];
          this.pollForUpdates(id);

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

  pollForUpdates(id) {

    this.getTranscriptionService.getDetails(id)
      .subscribe((retData) => {
        console.log(retData);
        let data = retData['data'][0];
        let id = data['call_id'];
        let remoteUrl = data['call_link'];
        let lastUpdated = data['last_updated'];
        let transcription = data['transcript'];
        let sentiment = data['sentiment'];
        let status = data['process_status'];

        this.speech = {
          id: id,
          transcription: transcription,
          sentiment: sentiment,
          status: status,
          localFileUrl: this.url,
          remoteUrl: remoteUrl,
          timeUpdated: lastUpdated
        };

        if (this.speech.status != 'gcp_complete') {
          console.log(this.speech.status + ' is the status and continue the polling');
          this.pollingHandler = setTimeout(handler => {
              return this.pollForUpdates(id);
            }, 2000);
        } else {
          console.log(this.speech.status + ' is the status and we are clearing timeout');
            clearTimeout(this.pollingHandler);
            return;
        }

      }, error1 => {

        this.error = JSON.stringify(error1);
      });

  } // pollforUpdates

}
