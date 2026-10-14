import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // sube a 50 usuarios
    { duration: '5m', target: 200 },  // sube a 200 usuarios
    { duration: '2m', target: 0 },    // baja a 0
  ],
};

export default function () {
  http.get('http://CdkSta-LB8A1-h1F5yNMld5EU-1317042205.us-east-1.elb.amazonaws.com');
  sleep(1);
}