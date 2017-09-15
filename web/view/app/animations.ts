import { AnimationEntryMetadata, 
         trigger, 
         state, 
         style, 
         transition, 
         animate } from '@angular/core';

export function FadeIn(name: string): AnimationEntryMetadata {
    return trigger( name, [
            state('false', style({opacity: 0})),
            state('true',  style({opacity: 1})),
            transition('0 => 1', animate( '100ms ease-in-out')),
            transition('1 => 0', animate( '100ms ease-in-out')),
        ]);
}