import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { StreamEvent } from '../models/product';

@Injectable({
  providedIn: 'root'
})
export class Streaming {
  
  connectStream(idea: string): Subject<StreamEvent> {
    const eventSubject = new Subject<StreamEvent>();
    const url = `http://localhost:8000/products/generate-stream`;
    
    const eventSource = new EventSource(url);
    
    eventSource.onmessage = (event) => {
      const data: StreamEvent = JSON.parse(event.data);
      eventSubject.next(data);
      
      if (data.type === 'complete' || data.type === 'error' || data.type === 'end') {
        eventSource.close();
        eventSubject.complete();
      }
    };
    
    eventSource.onerror = (error) => {
      eventSubject.error(error);
      eventSource.close();
    };
    
    return eventSubject;
  }
}