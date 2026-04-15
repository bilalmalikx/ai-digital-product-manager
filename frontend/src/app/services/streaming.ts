// streaming.service.ts
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { StreamEvent } from '../models/product';

@Injectable({
  providedIn: 'root'
})
export class StreamingService {
  
  connectStream(idea: string): Subject<StreamEvent> {
    const eventSubject = new Subject<StreamEvent>();
    const url = `http://127.0.0.1:8000/products/generate-stream?idea=${encodeURIComponent(idea)}`;
    
    const eventSource = new EventSource(url);
    
    eventSource.onmessage = (event) => {
      try {
        const data: StreamEvent = JSON.parse(event.data);
        eventSubject.next(data);
        
        if (data.type === 'complete' || data.type === 'error' || data.type === 'end') {
          eventSource.close();
          eventSubject.complete();
        }
      } catch (e) {
        console.error('Error parsing stream data:', e);
      }
    };
    
    eventSource.onerror = (error) => {
      console.error('EventSource error:', error);
      eventSubject.error(error);
      eventSource.close();
    };
    
    return eventSubject;
  }
}