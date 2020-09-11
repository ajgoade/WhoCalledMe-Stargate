import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from "../../../environments/environment";
import {TokenStorageService} from "../tokenStorage/token-storage.service";

const FILE_UPLOAD_API_ENDPOINT = environment.serverProtocol + '://' + environment.serverName + ':' +
  environment.serverPort + '/files/';

let httpOptions = {

};


@Injectable({
  providedIn: 'root'
})
export class UploadService {

  constructor(public httpClient: HttpClient,
              public tokenStorageService: TokenStorageService
              ) { }

  public uploadFile(soundFile, user, fileName) {
    const formData = new FormData();
    formData.append('audio_message', soundFile, fileName);

    httpOptions = {
      headers: new HttpHeaders({
        'Authorization': 'Bearer ' + this.tokenStorageService.getToken(),
        reportProgress: 'true',
        observe: 'events'
      })
    };

    return this.httpClient.post(FILE_UPLOAD_API_ENDPOINT, formData, httpOptions);

  }

}
