import { TestBed } from '@angular/core/testing';

import { Engagement } from './engagement';

describe('Engagement', () => {
  let service: Engagement;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Engagement);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
