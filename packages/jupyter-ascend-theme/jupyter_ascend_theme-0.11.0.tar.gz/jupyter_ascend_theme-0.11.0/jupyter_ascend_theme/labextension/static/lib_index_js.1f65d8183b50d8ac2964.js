"use strict";
(self["webpackChunkjupyter_ascend_theme"] = self["webpackChunkjupyter_ascend_theme"] || []).push([["lib_index_js"],{

/***/ "./lib/configuration.js":
/*!******************************!*\
  !*** ./lib/configuration.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   appConfig: () => (/* binding */ appConfig)
/* harmony export */ });
const appConfig = {
    appName: 'Insula Coding (Experiment)',
    header: {
        isVisible: true,
        getInsulaAppsMenuLinks: () => {
            const linksFromEnvVariables = window.__MENU_LINKS__;
            if (linksFromEnvVariables && linksFromEnvVariables.length > 0) {
                return linksFromEnvVariables;
            }
            else {
                let environmentNameFromUrl = undefined;
                const originUrl = window.location.origin;
                if (originUrl.toLowerCase().includes('earthcare')) {
                    environmentNameFromUrl = 'earthcare';
                }
                else if (originUrl.toLowerCase().includes('biomass')) {
                    environmentNameFromUrl = 'biomass';
                }
                if (environmentNameFromUrl) {
                    return [
                        {
                            label: 'Visualisation & Analytics (Perception)',
                            href: `https://${environmentNameFromUrl}.pal.maap.eo.esa.int/perception`
                        },
                        {
                            label: 'Processing (Intellect)',
                            href: `https://${environmentNameFromUrl}.pal.maap.eo.esa.int/intellect`
                        },
                        {
                            label: 'Account Management (Awareness)',
                            href: `https://${environmentNameFromUrl}.pal.maap.eo.esa.int/awareness`
                        },
                        {
                            label: 'Documentation',
                            href: `https://portal.maap.eo.esa.int/ini/services/PAL/${environmentNameFromUrl}/`
                        }
                    ];
                }
                else {
                    return undefined;
                }
            }
        }
        // otherInfoMenuLinks: [
        //   {
        //     label: 'Docs',
        //     href: '<Docs_link>'
        //   },
        //   {
        //     label: 'Support',
        //     href: '<Support_link>'
        //   }
        // ]
    }
};


/***/ }),

/***/ "./lib/icons.js":
/*!**********************!*\
  !*** ./lib/icons.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   Icons: () => (/* binding */ Icons)
/* harmony export */ });
/* eslint-disable @typescript-eslint/quotes */
const Icons = {
    CGILogo: `<svg xmlns="http://www.w3.org/2000/svg" width="1343" height="1344">
    <path d="M0 0h1343v1344H0V0z" fill="#FEFEFE" />
    <path
        d="M857.125 379.875h3.1c12.03.03 24.06.08 36.09.5l2.95.09c5.21.23 10.09.94 15.18 2.04 4.53.88 9.1 1.23 13.68 1.62.96.09 1.91.17 2.9.26 2.32.21 4.65.42 6.98.61v2c.87-.01.87-.01 1.75-.03 4.54-.05 8.77.12 13.25 1.03v2c1.23.13 2.47.25 3.74.38 5.8.64 11.52 1.63 17.26 2.62 1.99.34 3.99.67 6 1v2c3.96.5 3.96.5 8 1v2l2.74-.12c3.33.13 4.41.62 7.26 2.12 1.9.5 3.81.99 5.72 1.45 6.39 1.56 12.24 3.41 18.05 6.5 4.56 2.15 9.42 3.55 14.23 5.05v2h3v125c-1.99-.33-3.97-.65-6-1-.67-.99-1.32-1.98-2-3-2.73-1.6-2.73-1.6-5.88-3.06-1.05-.5-2.1-1.01-3.18-1.53-.97-.47-1.94-.93-2.94-1.41-1.34-.66-2.67-1.32-4-2v-2c-.95-.06-1.9-.12-2.88-.18-4.4-.6-7.92-2.56-11.79-4.66-2.13-1.06-4.01-1.69-6.33-2.16v-2c-1.99-.33-3.97-.65-6-1v-2c-.95-.08-1.9-.16-2.88-.24-4.24-.59-7.96-2.16-11.89-3.82-2.34-1.01-2.34-1.01-5.23-1.94v-2l-1.87-.14c-.81-.08-1.61-.15-2.45-.23-.8-.07-1.6-.14-2.42-.21-2.26-.42-2.26-.42-5.26-2.42-2.28-.66-2.28-.66-4.69-1.12-.81-.17-1.62-.34-2.45-.51-.62-.12-1.23-.24-1.86-.37v-2h-6v-2c-2.98-.32-5.95-.65-9-1v-2l-2.81-.18c-1.2-.08-2.4-.17-3.63-.25-1.79-.12-1.79-.12-3.62-.25-2.94-.32-2.94-.32-3.94-1.32-2.38-.35-4.75-.66-7.13-.93-3.89-.46-7.49-.95-11.24-2.09-4.6-1.23-8.95-1.44-13.7-1.6-1.48-.05-1.48-.05-2.99-.11-35.24-1.44-35.24-1.44-69.94 3.73-3.5.13-3.5.13-6 0v2c-4.46.5-4.46.5-9 1v2c-1.16.44-2.31.87-3.5 1.32-.73.27-1.46.55-2.21.83-1.47.55-2.95 1.09-4.43 1.62-3.11 1.12-5.83 2.21-8.68 3.92-2.18 1.31-2.18 1.31-5.18 1.31v2c-1.77.85-3.54 1.68-5.32 2.5-.98.47-1.97.93-2.99 1.41-2.69 1.09-2.69 1.09-5.69 1.09v2c-6.76 4-6.76 4-9 4v2c-1.32 1.63-1.32 1.63-3 3h-3c-.34 1-.66 1.99-1 3h-2v2c-1.65.34-3.3.66-5 1-.34 1-.66 1.99-1 3h-2c-.34 1-.66 1.99-1 3h-2c-.34 1-.66 1.99-1 3h-2c-.34 1-.66 1.99-1 3h-2c-.34 1-.66 1.99-1 3h-2c-.07.75-.13 1.49-.19 2.26-1.06 3.58-2.88 4.55-5.81 6.74-.34 1-.66 1.99-1 3h-2c-.34 1-.66 1.99-1 3h-2c-.34 1.65-.66 3.3-1 5h-2c-.34 1.99-.66 3.97-1 6h-2c-.25.87-.5 1.74-.76 2.63-1.32 3.58-3.12 6.22-5.24 9.37-1.89 3.98-3.34 7.65-4 12h-2v3h-2c-.66 3.97-1.32 7.92-2 12h-2c-.13 1.24-.25 2.48-.38 3.76-.41 3.67-.94 7.29-1.56 10.93-.26 1.56-.26 1.56-.52 3.14a249.1 249.1 0 01-1.12 6.07c-1.53 8.62-1.61 17.11-1.61 25.86v3.82c-.28 5.89-.28 5.89 1.19 11.42.19 1.49.34 2.98.46 4.48.08.9.16 1.8.24 2.73.15 1.88.31 3.76.46 5.64.51 5.87 1.43 11.42 2.84 17.15h2c1.33 6 2.66 12 4 18h2c.33 1.99.65 3.97 1 6h2c.33 2.64.65 5.28 1 8h2c.33 1.32.65 2.64 1 4h2c.33 1.99.65 3.97 1 6h2c.33 1.65.65 3.3 1 5h2c.59 1.1 1.19 2.19 1.81 3.32 1.49 2.63 2.99 4.6 5.19 6.68v2h2c.33 1 .65 1.99 1 3 1.65 1.35 3.32 2.68 5 4 1.33 1.67 2.66 3.34 4 5 .82.67 1.64 1.32 2.5 2 2.61 2.1 4.43 4.38 6.5 7 .65.33 1.31.67 2 1v2c.99.33 1.98.67 3 1v2h3c.61.79 1.23 1.57 1.87 2.38 2.27 2.81 3.73 3.59 7.13 4.62v2c1.98.33 3.96.67 6 1v2c1.64.33 3.29.67 5 1v2c1.31.33 2.63.67 4 1v2c1.98.33 3.96.67 6 1v2h3v2c.92.17.92.17 1.87.34 5.9 1.1 11.48 2.62 17.13 4.66v2c1.13.09 2.26.17 3.43.26 3.38.4 6 1.28 9.07 2.74 4.27 2.05 7.8 2.54 12.5 3 .9.33 1.81.67 2.74 1 4.17 1.29 8.21 1.49 12.55 1.76 2.71.24 2.71.24 5.71 1.24 2.45.13 4.87.19 7.32.21.73 0 1.46.01 2.21.02 2.39.02 4.77.02 7.15.03h2.45c13.63.01 27.49-.28 40.87-3.26l1-1c2.01-.23 4.03-.41 6.06-.56 1.65-.12 1.65-.12 3.35-.25.85-.06 1.7-.12 2.59-.19v-2h4v-2c2.3-.32 4.62-.66 7-1v-101h-88v-105h203c.08 70.44.08 70.44.09 99.79.01 6.72.01 13.44.01 20.16.01.84.01 1.69.01 2.55.01 13.61.02 27.23.04 40.84.02 13.96.03 27.92.03 41.88.01 8.62.01 17.24.03 25.86.01 5.9.01 11.81.01 17.71 0 3.41 0 6.82.01 10.23.01 3.7.01 7.39.01 11.08 0 1.63 0 1.63.01 3.29 0 .99 0 1.97-.01 2.98v2.58c-.24 2.05-.24 2.05-2.24 4.05-2.33.41-4.66.74-7 1v2c-1.99.34-3.97.66-6 1v2c-4.93 1.68-9.88 3.28-14.85 4.8-.69.21-1.38.42-2.09.64-.7.22-1.4.43-2.12.65-3.84 1.19-7.51 2.53-11.2 4.17-5.42 2.29-10.91 2.54-16.74 2.74v2c-8.83 3.6-17.55 5.09-27 6v2c-10.04 1.25-19.87 2.36-30 2v2c-.9.09-.9.09-1.81.17-2.69.26-5.38.51-8.07.77-1.41.13-1.41.13-2.84.27-.9.08-1.79.17-2.71.26-.83.08-1.66.16-2.51.24-2.12.19-2.12.19-4.06 1.29-1.37.16-2.74.25-4.11.32l-2.58.12-2.83.12c-.98.04-1.95.08-2.96.13-10.66.42-21.32.47-31.99.45-3.3-.01-6.6 0-9.9 0-9.63.01-19.24-.06-28.86-.58l-2.16-.12c-4.62-.29-9.05-.91-13.56-1.96-2.99-.69-6.01-1.08-9.05-1.48v-2c-1.56-.05-1.56-.05-3.15-.11-11.16-.49-20.06-2.7-30.38-6.97-3.76-1.39-7.54-2.15-11.47-2.92v-2c-2.98-.33-5.95-.65-9-1v-2c-1.99-.33-3.97-.65-6-1v-2c-1.17-.08-2.33-.17-3.52-.25-4.68-.59-8.18-2.31-12.24-4.62-.64-.35-1.29-.7-1.95-1.07-3.29-1.81-6.3-3.8-9.29-6.06-1-.33-1.99-.65-3-1v-2c-1.99-.33-3.97-.65-6-1v-2c-1.65-.33-3.3-.65-5-1v-2c-.97-.12-1.94-.24-2.94-.37-1.52-.31-1.52-.31-3.06-.63-.34-.66-.66-1.31-1-2-1-.32-1.99-.66-3-1v-2c-.77-.28-1.53-.57-2.32-.87-2.69-1.13-2.69-1.13-5.68-3.13v-2c-.81-.12-1.61-.24-2.44-.37-1.27-.31-1.27-.31-2.56-.63-.34-.66-.66-1.31-1-2-1-.32-1.99-.66-3-1-1.69-1.43-1.69-1.43-3-3v-2c-1.32-.32-2.64-.66-4-1v-2c-.62-.08-1.24-.16-1.88-.24-2.8-.99-2.87-2.16-4.12-4.76-2.02-1.13-2.02-1.13-4-2-.34-.66-.66-1.31-1-2-1-.32-1.99-.66-3-1-1.39-1.72-2.53-3.54-3.72-5.4-1.29-1.9-1.29-1.9-4.28-2.6-.44-.74-.87-1.48-1.32-2.24-2.06-3.36-4.67-5.26-7.68-7.76-1.26-2.24-1.26-2.24-2-4-.66-.32-1.32-.66-2-1v-3c-1-.32-1.99-.66-3-1v-2c-1-.32-1.99-.66-3-1v-2h-2c-.34-1.64-.66-3.29-1-5-1-.32-1.99-.66-3-1v-3h-2c-2.62-1.88-3-2.97-3.69-6.18-.11-.93-.21-1.86-.31-2.82h-2c-4-5.29-4-5.29-4-9h-2c-4-5.29-4-5.29-4-9h-2c-.34-1.98-.66-3.96-1-6h-2c-.68-1.43-1.34-2.87-2-4.31-.38-.8-.75-1.6-1.13-2.42-.87-2.27-.87-2.27-.87-5.27h-2c-.38-1.23-.38-1.23-.76-2.5-.95-2.66-1.93-4.89-3.24-7.37-1.71-3.3-2.65-6.38-3.44-9.99-.66-2.48-1.58-4.77-2.56-7.14-1.79-4.3-2.96-8.45-4-13-.95-3.4-1.91-6.74-3.13-10.06-.93-3.12-1.03-5.69-.87-8.94h-2c-.78-6.06-1.1-11.88-1-18h-2c-.91-11.59-1.16-23.12-1.14-34.75.01-2.81 0-5.61 0-8.42-.01-10.32.26-20.54 1.14-30.83h2c.1-1.17.2-2.35.31-3.56 1.09-9.92 3.47-19.71 5.69-29.44h2c.33-3.29.65-6.6 1-10h2c.49-3.96.49-3.96 1-8h2c.33-2.97.65-5.94 1-9h2l2-11h2c.1-.85.2-1.71.3-2.6.75-3.68 2.02-6.45 3.76-9.77.55-1.06 1.09-2.12 1.66-3.21.42-.8.84-1.59 1.28-2.42h2v-3h2c.11-.57.22-1.15.34-1.74.72-2.46 1.74-4.18 3.16-6.32 1.58-2.39 2.58-4.18 3.5-6.94 1.31-1.35 2.64-2.68 4-4 .99-1.48.99-1.48 2-3h2c.1-.72.2-1.45.31-2.19.75-3.06 1.86-5.02 3.62-7.62.53-.79 1.05-1.58 1.59-2.39.49-.59.97-1.19 1.48-1.8h2c.49-1.48.49-1.48 1-3h2v-3c1.18-1.37 1.18-1.37 3-3l2.31-2.31c1.41-1.41 2.83-2.82 4.27-4.2 2.73-2.64 5.02-4.86 6.42-8.49h2c.49-1.48.49-1.48 1-3h2v-2c1.79-1.58 1.79-1.58 4.18-3.37.82-.62 1.64-1.24 2.48-1.88.77-.58 1.54-1.15 2.34-1.75 3.55-2.55 3.55-2.55 6-6h3v-2c4.35-4 4.35-4 8-4 .33-.99.65-1.98 1-3 9.92-9 9.92-9 15-9v-2c.88-.43 1.77-.86 2.68-1.31 5.26-2.58 5.26-2.58 9.82-6.19 4-4 7.95-4.95 13.5-5.5v-2c2.97-.49 2.97-.49 6-1v-2c2.97-.49 2.97-.49 6-1v-2c2.97-.49 2.97-.49 6-1v-2c5.12-2.45 9.33-3.5 15-4v-2c2.97-.32 5.94-.66 9-1v-2c4.45-.49 4.45-.49 9-1v-2c.77-.18 1.54-.36 2.34-.55 6.89-1.62 6.89-1.62 13.53-4.01 4.88-1.98 10.05-2.38 15.25-3.01 2.77-.12 2.77-.12 3.88-1.43 2.31-.32 4.63-.51 6.96-.71 2.03-.08 2.03-.08 3.04-1.29 5.96-1.01 12.08-1.25 18.11-1.55 1.29-.06 1.29-.06 2.6-.13 10.47-.47 20.93-.47 31.41-.44z"
        fill="#E11937" />
    <path
        d="M316.967 378.839l3-.03c1.08 0 2.15-.01 3.25-.01 1.12-.01 2.24-.02 3.39-.02 3.63-.02 7.26-.03 10.89-.03h3.71c37.43-.02 37.43-.02 52.79 3.25l1 1c2.23.31 4.46.57 6.69.81 5.29.63 10.2 1.62 15.31 3.19 7.29 2.23 14.44 3.2 22 4v2h6v2l9 1v2l2.35.08c6.01.33 10.6.92 15.83 3.93 2.82 1.53 5.72 2.22 8.82 2.99v2c3.96.5 3.96.5 8 1v2l9 1v2l6 1v2c1.06.1 2.11.21 3.19.31 3.81.69 5.78 1.35 8.81 3.69.62 2.32.62 2.32.6 5.11.01 1.58.01 1.58.03 3.2l-.06 3.51v3.69c0 3.35-.02 6.69-.06 10.04-.03 3.49-.03 6.99-.04 10.48-.02 6.62-.06 13.24-.11 19.86-.05 7.54-.08 15.07-.11 22.61-.05 15.5-.14 31-.25 46.5-2.64-.56-3.92-.94-6.06-2.69-3.55-2.79-7.32-4.76-11.32-6.84-2.62-1.47-2.62-1.47-4.6-2.98-2.45-1.81-4.98-2.95-7.77-4.18-.98-.43-1.97-.87-2.98-1.32-1.12-.49-1.12-.49-2.27-.99v-2h-3v-2c-.8-.06-1.61-.12-2.43-.19-3.21-.73-4.98-1.5-7.75-3.12-4.26-2.49-8.56-4.16-13.22-5.77-3.28-1.16-6.42-2.51-9.6-3.92v-2l-6-1v-2l-9-1v-2l-9-1v-2l-9-1v-2c-.63-.05-1.25-.1-1.9-.15-4.11-.36-8.06-.74-12.03-1.85-3.24-.89-6.34-1.25-9.69-1.5-3.05-.23-5.4-.51-8.31-1.5-9.16-2.99-19.63-2.16-29.19-2.13-2.11.01-4.22 0-6.33-.01-18.46-.05-18.46-.05-36.55 3.14-2.36.15-4.62.1-7 0v2l-11 1v2c-4.45.5-4.45.5-9 1v2l-8 1v2c-1.24.51-1.24.51-2.52 1.02-1.08.45-2.17.9-3.29 1.36-1.08.44-2.16.88-3.27 1.33-3.02 1.24-3.02 1.24-5.92 3.29h-3v2l-6.05 1.17c-2.11.64-2.11.64-2.81 2.66-1.71 3.27-4.34 4.31-7.51 6.11-4.58 2.6-7.45 4.89-10.63 9.06h-2l-1 3h-3l-1 3h-2l-1 3h-2v2h-2l-1 4h-2l-1 3h-2l-.18 2.25c-.82 2.75-.82 2.75-3.13 4.56-3.52 2.87-4.91 6.09-6.69 10.19h-2c-.12.97-.24 1.94-.37 2.94-.21 1.01-.41 2.02-.63 3.06l-2 1c-.7 1.65-1.35 3.32-2 5-1 2.06-2.04 4.1-3.09 6.13-1.03 2.02-1.03 2.02-1.91 4.87h-2l-1 7h-2l-1 6h-2l-1 12h-2v6h-2c-1.11 15.21-1.11 30.38-1.06 45.63.01 2.47.01 4.94.01 7.41.02 5.99.03 11.97.05 17.96h2c.12.8.25 1.59.37 2.42 1.02 6.56 1.02 6.56 2.76 12.96 1 2.99 1.02 5.48.87 8.62h2c.68 1.75 1.34 3.5 2 5.25.37.98.75 1.95 1.13 2.95.87 2.8.87 2.8.87 6.8h2l1 6h2l1 6h2c.27.57.53 1.13.81 1.72.35.73.7 1.46 1.07 2.22.52 1.09.52 1.09 1.05 2.21.94 2.01.94 2.01 3.07 2.85.93 1.71.93 1.71 1.88 3.81 1.62 3.41 3.4 5.56 6.12 8.19.35.89.7 1.77 1.07 2.69.31.76.61 1.52.93 2.31l3 1c1.61 1.56 1.61 1.56 3.19 3.44.53.62 1.06 1.23 1.61 1.87 1.2 1.69 1.2 1.69 1.2 3.69.84.09.84.09 1.69.19 3.29 1.15 4.97 3.29 7.31 5.81.6.56 1.2 1.11 1.82 1.69 1.18 1.31 1.18 1.31 1.18 3.31.87.43.87.43 1.75.88 2.09 1.04 4.17 2.08 6.25 3.12v2h3l1 2c1.65.72 3.31 1.39 5 2v2h2v2l7 2v2h5l1 3h3v2c.56.1 1.12.2 1.69.3 4.07.8 7.6 1.7 11.25 3.7 3.78 2.04 7.34 2.72 11.55 3.43 2.61.59 4.74 1.48 7.14 2.63 4.21 2.02 7.74 2.48 12.37 2.94 1.32.49 1.32.49 2.66.99 4.27 1.29 8.27 1.48 12.72 1.64.91.03 1.82.07 2.76.11 32.73 1.52 32.73 1.52 64.95-3.12 3.05-.65 5.8-.73 8.91-.62v-2c.93-.16.93-.16 1.87-.33 5.22-.98 10.14-2.25 15.15-4 2.3-.77 4.59-1.28 6.98-1.67v-2l6-1v-2l9-1v-2l6-1v-2l6-1v-2l6-1v-2l4-1v-2l5-1v-2l6-1v-2c.57-.26 1.14-.53 1.72-.8.73-.36 1.46-.71 2.22-1.07.73-.35 1.46-.7 2.22-1.06 2.01-.94 2.01-.94 2.84-3.07 2.57-.62 2.57-.62 5-1l1-3h3v-2c1.67-2.1 2.91-2.96 5.44-3.94 2.97-1.23 4.37-2.73 6.56-5.06 4.56-4 4.56-4 8-4l1-3h2l1-3h2v129l-9 3v2c-.96.45-1.93.9-2.93 1.36-1.31.61-2.63 1.22-3.94 1.83-1.03.47-1.03.47-2.07.96-3.91 1.82-7.75 3.71-11.56 5.73-3.9 1.99-7.13 2.84-11.5 3.12v2c-5.12 2.46-9.34 3.5-15 4v2l-9 1v2c-.88.27-1.76.53-2.66.81-1.17.35-2.33.7-3.52 1.07-1.15.34-2.3.69-3.48 1.05-2.03.65-4.04 1.36-6.02 2.15-2.79 1.11-5.62 1.68-8.55 2.28-3.34.77-6.6 1.75-9.89 2.7-7.66 2.09-14.95 2.72-22.88 2.94v2c-.9.08-.9.08-1.82.17-2.7.25-5.41.51-8.11.77-1.42.13-1.42.13-2.87.26-1.35.13-1.35.13-2.72.27-1.25.11-1.25.11-2.53.23-1.95.1-1.95.1-2.95 1.3-7.2 1.06-14.49 1.15-21.75 1.13-1.49.01-1.49.01-3 .01-2.07 0-4.15 0-6.22-.01-3.12 0-6.24 0-9.36.01-30.65.01-30.65.01-42.67-3.14-1.39-.22-2.78-.4-4.18-.53-.7-.06-1.39-.13-2.11-.2-1.06-.1-1.06-.1-2.14-.21-5.46-.57-10.41-1.34-15.56-3.33-3.57-1.3-7.29-1.98-11.01-2.73v-2l-9-1v-2l-9-1v-2l-6-1v-2l-9-1v-2l-6-1v-2c-.8-.08-1.61-.16-2.43-.25-4.53-.95-8.41-2.76-12.57-4.75v-2h-3v-2l-6-1v-2c-.8-.12-1.61-.25-2.43-.37-.85-.21-1.7-.42-2.57-.63l-1-2-3-1v-2l-6-1v-2c-.76-.1-1.52-.21-2.31-.31-2.87-.74-3.92-1.36-5.69-3.69v-2c-.72-.06-1.44-.12-2.18-.19-3.7-1.06-5.35-2.92-7.82-5.81v-2c-.82-.18-1.65-.37-2.5-.56-4.03-1.66-6.51-3.84-9.66-6.78-1.94-1.83-1.94-1.83-4.84-3.66v-2l-3-1v-2l-3-1v-2l-3-1v-2l-3-1v-2l-3-1v-2l-3-1v-2l-3-1v-2l-3-1v-2h-2c-1.62-1.31-1.62-1.31-3-3v-3h-2c-2-3-2-3-2-6l-3-1v-2h-2c-3.76-3.11-6.11-7.22-7-12h-2c-.98-1.75-1.96-3.5-2.93-5.25-.55-.97-1.09-1.95-1.66-2.95-1.17-2.33-1.93-4.25-2.41-6.8h-2c-.08-.78-.16-1.57-.25-2.37-.24-.87-.49-1.74-.75-2.63-1.32-.68-2.66-1.35-4-2-1.49-2.91-2-4.71-2-8h-2c-.23-.69-.46-1.38-.7-2.09-1.98-5.71-4.19-10.87-7.34-16.03-.96-1.88-.96-1.88-.96-4.88h-2l-1-9h-2l-1-6h-2l-1-12h-2c-1.33-8-2.66-16-4-24h-2c-1.26-8.78-1.16-17.55-1.16-26.41-.01-1.69-.01-3.38-.01-5.07-.01-3.53-.01-7.07-.01-10.6 0-4.51-.02-9.02-.03-13.53-.01-3.49-.02-6.98-.02-10.47 0-1.66 0-3.32-.01-4.98-.03-8.22-.01-15.96 2.24-23.94.36-2 .69-4 1-6 .82-5.05 1.84-10.01 3-15h2l1-12h2c.09-.81.18-1.62.26-2.46 1.02-7.96 3.01-14.43 6.74-21.54h2l2-11h2c.14-.57.27-1.14.41-1.73.59-2.25 1.33-4.35 2.16-6.52.27-.71.53-1.41.81-2.14.21-.53.41-1.06.62-1.61h2v-3h2c.13-.58.25-1.15.38-1.74.63-2.3 1.48-4.21 2.56-6.32.34-.67.68-1.34 1.03-2.04 1.03-1.9 1.03-1.9 3.03-4.9h2c.11-.74.21-1.48.32-2.25.73-2.95 1.63-4.53 3.68-6.75h2l1-5 3-1v-3h2c.5-1.48.5-1.48 1-3h2v-3c.73-.56 1.45-1.11 2.19-1.69 3.16-2.6 4.72-5.17 6.7-8.7.37-.53.73-1.06 1.11-1.61h2c.5-1.48.5-1.48 1-3h2c.5-1.48.5-1.48 1-3h2c.5-1.48.5-1.48 1-3h2c.5-1.48.5-1.48 1-3h2c.5-1.48.5-1.48 1-3h2c.5-1.48.5-1.48 1-3h2c.5-1.48.5-1.48 1-3h2v-2c2.62-2.3 5.34-4.22 8.25-6.12 2.81-1.59 2.81-1.59 3.75-3.88h3l1-3h2v-2c5.3-4 5.3-4 9-4v-2c1.88-2.61 2.98-2.99 6.19-3.69 1.39-.15 1.39-.15 2.81-.31v-2c6.75-4 6.75-4 9-4v-2h3v-2c2.48-.49 2.48-.49 5-1v-2l9-2v-2c1.44-.67 2.88-1.34 4.32-2 1.2-.56 1.2-.56 2.42-1.12 2.26-.88 2.26-.88 5.26-.88v-2h3v-2c.64-.2 1.28-.41 1.94-.62.82-.27 1.65-.54 2.5-.82.82-.26 1.65-.53 2.5-.8 2.03-.58 2.03-.58 3.06-1.76 1.67-.04 3.34-.04 5 0v-2c9.41-2.29 9.41-2.29 14-2v-2c4.95-.49 4.95-.49 10-1v-2l12-1v-2c.85-.11 1.69-.22 2.57-.33 6.58-.92 12.3-2.15 18.43-4.67 5.42-1.35 10.96-1.41 16.51-1.72 3.26-.15 3.26-.15 5.4-.79 2.41-.56 4.59-.63 7.06-.65zM1131 390h115v535h-115V390z"
        fill="#E11A38" />
    <path
        d="M514 758h2v129c-2.48.99-2.48.99-5 2v-2h3c-.01-.66-.01-1.32-.02-2-.15-16-.29-32.01-.42-48.02l-.21-23.22-.18-20.23c-.02-3.57-.06-7.15-.09-10.72-.04-3.98-.07-7.96-.1-11.95-.01-1.19-.03-2.38-.04-3.61-.01-1.08-.02-2.16-.02-3.27l-.03-2.86C513 759 513 759 514 758z"
        fill="#EC7083" />
    <path d="M516 420h1l1 127h-4v-2h2V420z" fill="#FBE1E5" />
    <path d="M925 384l13 1v2l1.76-.04c4.54-.05 8.77.12 13.24 1.04v2l-21-2v-2h-6l-1-2z" fill="#EC7385" />
    <path d="M819 381l-1 2h-9v2l-15 1 1-2c2.03-.38 2.03-.38 4.5-.56 3.05-.02 3.05-.02 5.5-1.44 4.62-.77 9.32-1.15 14-1z"
        fill="#E8546A" />
    <path d="M737 530h2c-1.45 5.33-5.08 8.36-9 12l-3-1c2.69-3.59 5.48-6.24 9-9l1-2z" fill="#F6BFC7" />
    <path
        d="M591 527l2 1-4 9h-2l-1 7-4 1c3.47-7.42 3.47-7.42 7-15h2v-3zM264 926c12.67.78 12.67.78 18 3v2c-6.44-.51-11.96-1.73-18-4v-1z"
        fill="#EB687C" />
    <path d="M970 393l10 1v2l8 1v1c-4.4.17-7.15.05-11-2-2.32-.39-4.66-.73-7-1v-2z" fill="#ED7C8D" />
    <path d="M429 390l10 1v2h6v2l-9-1v-2h-7v-2z" fill="#EB667A" />
    <path d="M626 479l1 3a138.67 138.67 0 01-5 5h-2c0-2 0-2 1.31-3.44.56-.51 1.12-1.03 1.69-1.56l1.69-1.69L626 479z"
        fill="#E53E57" />
    <path d="M221 402v2h-2v2l-6 1v-2h3v-2c3-1 3-1 5-1z" fill="#EA6175" />
    <path d="M424 813v2c-4.45 1.49-4.45 1.49-9 3v-2h2v-2c4.75-1 4.75-1 7-1z" fill="#F5B8C1" />
    <path
        d="M804 494v2c-1.29.53-2.58 1.05-3.88 1.56-1.07.44-1.07.44-2.17.88C796 499 796 499 794 498l4-1v-2c2.08-.55 3.84-1 6-1z"
        fill="#F6BBC4" />
</svg>`,
    MenuIcon: `<svg viewBox="64 64 896 896" focusable="false" data-icon="menu" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M904 160H120c-4.4 0-8 3.6-8 8v64c0 4.4 3.6 8 8 8h784c4.4 0 8-3.6 8-8v-64c0-4.4-3.6-8-8-8zm0 624H120c-4.4 0-8 3.6-8 8v64c0 4.4 3.6 8 8 8h784c4.4 0 8-3.6 8-8v-64c0-4.4-3.6-8-8-8zm0-312H120c-4.4 0-8 3.6-8 8v64c0 4.4 3.6 8 8 8h784c4.4 0 8-3.6 8-8v-64c0-4.4-3.6-8-8-8z"></path></svg>`,
    CloseIcon: `<svg fill-rule="evenodd" viewBox="64 64 896 896" focusable="false" data-icon="close" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M799.86 166.31c.02 0 .04.02.08.06l57.69 57.7c.04.03.05.05.06.08a.12.12 0 010 .06c0 .03-.02.05-.06.09L569.93 512l287.7 287.7c.04.04.05.06.06.09a.12.12 0 010 .07c0 .02-.02.04-.06.08l-57.7 57.69c-.03.04-.05.05-.07.06a.12.12 0 01-.07 0c-.03 0-.05-.02-.09-.06L512 569.93l-287.7 287.7c-.04.04-.06.05-.09.06a.12.12 0 01-.07 0c-.02 0-.04-.02-.08-.06l-57.69-57.7c-.04-.03-.05-.05-.06-.07a.12.12 0 010-.07c0-.03.02-.05.06-.09L454.07 512l-287.7-287.7c-.04-.04-.05-.06-.06-.09a.12.12 0 010-.07c0-.02.02-.04.06-.08l57.7-57.69c.03-.04.05-.05.07-.06a.12.12 0 01.07 0c.03 0 .05.02.09.06L512 454.07l287.7-287.7c.04-.04.06-.05.09-.06a.12.12 0 01.07 0z"></path></svg>`,
    UserIcon: `<svg viewBox="64 64 896 896" focusable="false" data-icon="user" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M858.5 763.6a374 374 0 00-80.6-119.5 375.63 375.63 0 00-119.5-80.6c-.4-.2-.8-.3-1.2-.5C719.5 518 760 444.7 760 362c0-137-111-248-248-248S264 225 264 362c0 82.7 40.5 156 102.8 201.1-.4.2-.8.3-1.2.5-44.8 18.9-85 46-119.5 80.6a375.63 375.63 0 00-80.6 119.5A371.7 371.7 0 00136 901.8a8 8 0 008 8.2h60c4.4 0 7.9-3.5 8-7.8 2-77.2 33-149.5 87.8-204.3 56.7-56.7 132-87.9 212.2-87.9s155.5 31.2 212.2 87.9C779 752.7 810 825 812 902.2c.1 4.4 3.6 7.8 8 7.8h60a8 8 0 008-8.2c-1-47.8-10.9-94.3-29.5-138.2zM512 534c-45.9 0-89.1-17.9-121.6-50.4S340 407.9 340 362c0-45.9 17.9-89.1 50.4-121.6S466.1 190 512 190s89.1 17.9 121.6 50.4S684 316.1 684 362c0 45.9-17.9 89.1-50.4 121.6S557.9 534 512 534z"></path></svg>`,
    InfoIcon: `<svg viewBox="64 64 896 896" focusable="false" data-icon="info-circle" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z"></path><path d="M464 336a48 48 0 1096 0 48 48 0 10-96 0zm72 112h-48c-4.4 0-8 3.6-8 8v272c0 4.4 3.6 8 8 8h48c4.4 0 8-3.6 8-8V456c0-4.4-3.6-8-8-8z"></path></svg>`,
    AppsIcon: `<svg viewBox="64 64 896 896" focusable="false" data-icon="appstore" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M864 144H560c-8.8 0-16 7.2-16 16v304c0 8.8 7.2 16 16 16h304c8.8 0 16-7.2 16-16V160c0-8.8-7.2-16-16-16zm0 400H560c-8.8 0-16 7.2-16 16v304c0 8.8 7.2 16 16 16h304c8.8 0 16-7.2 16-16V560c0-8.8-7.2-16-16-16zM464 144H160c-8.8 0-16 7.2-16 16v304c0 8.8 7.2 16 16 16h304c8.8 0 16-7.2 16-16V160c0-8.8-7.2-16-16-16zm0 400H160c-8.8 0-16 7.2-16 16v304c0 8.8 7.2 16 16 16h304c8.8 0 16-7.2 16-16V560c0-8.8-7.2-16-16-16z"></path></svg>`
};


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _configuration__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./configuration */ "./lib/configuration.js");
/* harmony import */ var _pallettes__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./pallettes */ "./lib/pallettes/dark-pallette-setter.js");
/* harmony import */ var _pallettes__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./pallettes */ "./lib/pallettes/light-pallette-setter.js");
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./utils */ "./lib/utils.js");




(0,_utils__WEBPACK_IMPORTED_MODULE_4__.initiAppFaviconAndTitle)();
/**
 * Initialization data for the jupyter_ascend_theme extension.
 */
const plugin = {
    id: 'jupyter_ascend_theme:plugin',
    description: 'The JupyterLab ASCEND theme',
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.IThemeManager],
    activate: (app, manager) => {
        app.started.then(() => {
            if (_configuration__WEBPACK_IMPORTED_MODULE_1__.appConfig.header.isVisible) {
                (0,_utils__WEBPACK_IMPORTED_MODULE_4__.initAppHeader)();
            }
        });
        /**
         * Due to the current limitation of not being able to register multiple themes
         * [https://github.com/jupyterlab/jupyterlab/issues/14202]
         * in the same extension when each theme has its own separate CSS file, we
         * handle theme variants by storing the color palette in TypeScript files and
         * loading them dynamically through a script. This approach allows us to load
         * a base theme ('jupyter-cgi-theme/index.css') and then override the necessary color properties
         * based on the selected palette.
         *
         * * Note: In development mode, the path to 'index.css' might differ because the plugin
         * expects the CSS file to be located in the mounted app's root folder (lib).
         */
        const pallettesSetters = [
            _pallettes__WEBPACK_IMPORTED_MODULE_3__.LightPalletteSetter,
            _pallettes__WEBPACK_IMPORTED_MODULE_2__.DarkPalletteSetter
        ];
        const baseTheme = 'jupyter_ascend_theme/index.css';
        pallettesSetters.forEach(Pallette => {
            const pallette = new Pallette();
            manager.register({
                name: pallette.name,
                isLight: pallette.type === 'light',
                load: () => {
                    pallette.setColorPallette();
                    return manager.loadCSS(baseTheme);
                },
                unload: () => Promise.resolve(undefined)
            });
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/pallettes/dark-pallette-setter.js":
/*!***********************************************!*\
  !*** ./lib/pallettes/dark-pallette-setter.js ***!
  \***********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   DarkPalletteSetter: () => (/* binding */ DarkPalletteSetter)
/* harmony export */ });
class DarkPalletteSetter {
    constructor() {
        this.name = 'ASCEND Theme Dark';
        this.type = 'dark';
    }
    setColorPallette() {
        /**
         * Borders
         */
        document.documentElement.style.setProperty('--jp-border-color0', 'var(--md-grey-200)');
        document.documentElement.style.setProperty('--jp-border-color1', 'var(--md-grey-300)');
        document.documentElement.style.setProperty('--jp-border-color2', 'var(--md-grey-400)');
        document.documentElement.style.setProperty('--jp-border-color3', 'var(--md-grey-400)');
        /**
         * Defaults use Material Design specification
         */
        document.documentElement.style.setProperty('--jp-ui-font-color0', 'rgba(255, 255, 255, 1)');
        document.documentElement.style.setProperty('--jp-ui-font-color1', 'rgba(255, 255, 255, 1)');
        document.documentElement.style.setProperty('--jp-ui-font-color2', 'rgba(255, 255, 255, 0.9)');
        document.documentElement.style.setProperty('--jp-ui-font-color3', 'rgba(255, 255, 255, 0.8)');
        /**
         * Defaults use Material Design specification
         */
        document.documentElement.style.setProperty('--jp-content-font-color0', 'rgba(255, 255, 255, 1)');
        document.documentElement.style.setProperty('--jp-content-font-color1', 'rgba(255, 255, 255, 0.9)');
        document.documentElement.style.setProperty('--jp-content-font-color2', 'rgba(255, 255, 255, 0.8)');
        document.documentElement.style.setProperty('--jp-content-font-color3', 'rgba(255, 255, 255, 0.8)');
        /**
         * Layout
         */
        document.documentElement.style.setProperty('--jp-layout-color0', 'var(--ascend-darker-blue)');
        document.documentElement.style.setProperty('--jp-layout-color1', 'var(--ascend-darker-blue)');
        document.documentElement.style.setProperty('--jp-layout-color2', 'var(--ascend-dark-blue)');
        document.documentElement.style.setProperty('--jp-layout-color3', 'var(--ascend-dark-blue)');
        document.documentElement.style.setProperty('--jp-layout-color4', 'var(--ascend-dark-magenta)');
        /**
         * Inverse Layout
         */
        document.documentElement.style.setProperty('--jp-inverse-layout-color0', 'rgb(255, 255, 255)');
        document.documentElement.style.setProperty('--jp-inverse-layout-color1', 'rgb(255, 255, 255)');
        document.documentElement.style.setProperty('--jp-inverse-layout-color2', 'rgba(255, 255, 255, 0.87)');
        document.documentElement.style.setProperty('--jp-inverse-layout-color3', 'rgba(255, 255, 255, 0.87)');
        document.documentElement.style.setProperty('--jp-inverse-layout-color4', 'rgba(255, 255, 255, 0.87)');
        /**
         * State colors (warn, error, success, info)
         */
        document.documentElement.style.setProperty('--jp-warn-color0', 'var--ascend-dark-magenta)');
        document.documentElement.style.setProperty('--jp-warn-color1', 'var(--ascend-magenta)');
        document.documentElement.style.setProperty('--jp-warn-color2', 'var(--ascend-magenta)');
        document.documentElement.style.setProperty('--jp-warn-color3', 'var(--ascend-neutral-magenta)');
        /**
         * Cell specific styles
         */
        document.documentElement.style.setProperty('--jp-cell-editor-background', '#353535');
        document.documentElement.style.setProperty('--jp-cell-prompt-not-active-font-color', 'var(--md-grey-200)');
        /**
         * Rendermime styles
         */
        document.documentElement.style.setProperty('--jp-rendermime-error-background', 'var(--ascend-dark-blue)');
        document.documentElement.style.setProperty('--jp-rendermime-table-row-background', 'var(--md-grey-800)');
        document.documentElement.style.setProperty('--jp-rendermime-table-row-hover-background', 'var(--md-grey-700)');
        /**
         * Code mirror specific styles
         */
        document.documentElement.style.setProperty('--jp-mirror-editor-operator-color', '#a2f');
        document.documentElement.style.setProperty('--jp-mirror-editor-meta-color', '#a2f');
        document.documentElement.style.setProperty('--jp-mirror-editor-attribute-color', 'rgb(255, 255, 255)');
    }
}


/***/ }),

/***/ "./lib/pallettes/light-pallette-setter.js":
/*!************************************************!*\
  !*** ./lib/pallettes/light-pallette-setter.js ***!
  \************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   LightPalletteSetter: () => (/* binding */ LightPalletteSetter)
/* harmony export */ });
class LightPalletteSetter {
    constructor() {
        this.name = 'ASCEND Theme Light';
        this.type = 'light';
    }
    setColorPallette() {
        /**
         * Borders
         */
        document.documentElement.style.setProperty('--jp-border-color0', 'var(--md-grey-400)');
        document.documentElement.style.setProperty('--jp-border-color1', 'var(--md-grey-400)');
        document.documentElement.style.setProperty('--jp-border-color2', 'var(--md-grey-300)');
        document.documentElement.style.setProperty('--jp-border-color3', 'var(--md-grey-200)');
        /**
         * Defaults use Material Design specification
         */
        document.documentElement.style.setProperty('--jp-ui-font-color0', 'rgba(0, 0, 0, 1)');
        document.documentElement.style.setProperty('--jp-ui-font-color1', 'rgba(0, 0, 0, 0.87)');
        document.documentElement.style.setProperty('--jp-ui-font-color2', 'rgba(0, 0, 0, 0.54)');
        document.documentElement.style.setProperty('--jp-ui-font-color3', 'rgba(0, 0, 0, 0.38)');
        /**
         * Defaults use Material Design specification
         */
        document.documentElement.style.setProperty('--jp-content-font-color0', 'rgba(0, 0, 0, 1)');
        document.documentElement.style.setProperty('--jp-content-font-color1', 'rgba(0, 0, 0, 0.87)');
        document.documentElement.style.setProperty('--jp-content-font-color2', 'rgba(0, 0, 0, 0.54)');
        document.documentElement.style.setProperty('--jp-content-font-color3', 'rgba(0, 0, 0, 0.38)');
        /**
         * Layout
         */
        document.documentElement.style.setProperty('--jp-layout-color0', 'var(--ascend-white)');
        document.documentElement.style.setProperty('--jp-layout-color1', 'var(--ascend-white)');
        document.documentElement.style.setProperty('--jp-layout-color2', 'var(--ascend-gray)');
        document.documentElement.style.setProperty('--jp-layout-color3', 'var(--ascend-gray)');
        document.documentElement.style.setProperty('--jp-layout-color4', 'var(--ascend-neutral-rose)');
        /**
         * Inverse Layout
         */
        document.documentElement.style.setProperty('--jp-inverse-layout-color0', '#111');
        document.documentElement.style.setProperty('--jp-inverse-layout-color1', 'var(--md-grey-900)');
        document.documentElement.style.setProperty('--jp-inverse-layout-color2', 'var(--md-grey-800)');
        document.documentElement.style.setProperty('--jp-inverse-layout-color3', 'var(--md-grey-700)');
        document.documentElement.style.setProperty('--jp-inverse-layout-color4', 'var(--md-grey-600)');
        /**
         * State colors (warn, error, success, info)
         */
        document.documentElement.style.setProperty('--jp-warn-color0', 'var(--ascend-dark-magenta)');
        document.documentElement.style.setProperty('--jp-warn-color1', 'var(--ascend-magenta)');
        document.documentElement.style.setProperty('--jp-warn-color2', 'var(--ascend-magenta)');
        document.documentElement.style.setProperty('--jp-warn-color3', 'var(--ascend-neutral-magenta)');
        /**
         * Cell specific styles
         */
        document.documentElement.style.setProperty('--jp-cell-editor-background', 'var(--md-grey-100)');
        document.documentElement.style.setProperty('--jp-cell-prompt-not-active-font-color', 'var(--md-grey-700)');
        /**
         * Rendermime styles
         */
        document.documentElement.style.setProperty('--jp-rendermime-error-background', '#fdd');
        document.documentElement.style.setProperty('--jp-rendermime-table-row-background', 'var(--md-grey-100)');
        document.documentElement.style.setProperty('--jp-rendermime-table-row-hover-background', 'var(--md-grey-200)');
        /**
         * Code mirror specific styles
         */
        document.documentElement.style.setProperty('--jp-mirror-editor-operator-color', '#a2f');
        document.documentElement.style.setProperty('--jp-mirror-editor-meta-color', '#a2f');
        document.documentElement.style.setProperty('--jp-mirror-editor-attribute-color', '#999');
    }
}


/***/ }),

/***/ "./lib/utils.js":
/*!**********************!*\
  !*** ./lib/utils.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   initAppHeader: () => (/* binding */ initAppHeader),
/* harmony export */   initAppLogo: () => (/* binding */ initAppLogo),
/* harmony export */   initiAppFaviconAndTitle: () => (/* binding */ initiAppFaviconAndTitle)
/* harmony export */ });
/* harmony import */ var _configuration__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./configuration */ "./lib/configuration.js");
/* harmony import */ var _icons__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./icons */ "./lib/icons.js");
/* harmony import */ var _style_apple_touch_icon_png__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../style/apple-touch-icon.png */ "./style/apple-touch-icon.png");
/* harmony import */ var _style_favicon_png__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../style/favicon.png */ "./style/favicon.png");
/* harmony import */ var _style_logo_png__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../style/logo.png */ "./style/logo.png");





/**
 * Overrides the default document title and favicon.
 */
const initiAppFaviconAndTitle = () => {
    const head = document.head;
    const iconLinks = head.querySelectorAll('link[rel="icon"]');
    const shortcutIconLinks = head.querySelectorAll('link[rel="shortcut icon"]');
    const appleTouchIconLinks = head.querySelectorAll('link[rel="apple-touch-icon"]');
    const busyIconLinks = head.querySelectorAll('link[type="image/x-icon"]');
    // Existent favicons set by JupyterLab
    [
        ...Array.from(iconLinks),
        ...Array.from(shortcutIconLinks),
        ...Array.from(appleTouchIconLinks),
        ...Array.from(busyIconLinks)
    ].forEach(favicon => {
        if (head.contains(favicon)) {
            head.removeChild(favicon);
        }
    });
    const linkIcon = document.createElement('link');
    linkIcon.rel = 'icon';
    linkIcon.type = 'image/png';
    linkIcon.href = _style_favicon_png__WEBPACK_IMPORTED_MODULE_3__;
    linkIcon.setAttribute('sizes', '32x32');
    head.appendChild(linkIcon);
    const linkShortCut = document.createElement('link');
    linkShortCut.rel = 'shortcut icon';
    linkShortCut.type = 'image/png';
    linkShortCut.href = _style_favicon_png__WEBPACK_IMPORTED_MODULE_3__;
    linkShortCut.setAttribute('sizes', '32x32');
    head.appendChild(linkShortCut);
    const linkAppleTouch = document.createElement('link');
    linkAppleTouch.rel = 'apple-touch-icon';
    linkAppleTouch.href = _style_apple_touch_icon_png__WEBPACK_IMPORTED_MODULE_2__;
    linkAppleTouch.setAttribute('sizes', '180x180');
    head.appendChild(linkAppleTouch);
    const svgDataUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(_icons__WEBPACK_IMPORTED_MODULE_1__.Icons.CGILogo)}`;
    const linkMaskIcon = document.createElement('link');
    linkMaskIcon.rel = 'mask-icon';
    linkMaskIcon.type = 'image/svg+xml';
    linkMaskIcon.color = '#00ae9d';
    linkMaskIcon.href = svgDataUrl;
    head.appendChild(linkMaskIcon);
    Object.defineProperty(document, 'title', {
        set(_arg) {
            var _a, _b;
            (_b = (_a = Object.getOwnPropertyDescriptor(Document.prototype, 'title'
            // Edit the document.title property setter,
            // call the original setter function for document.title and make sure 'this' is set to the document object,
            // then overrides the value to set
            )) === null || _a === void 0 ? void 0 : _a.set) === null || _b === void 0 ? void 0 : _b.call(document, _configuration__WEBPACK_IMPORTED_MODULE_0__.appConfig.appName);
        },
        configurable: true
    });
};
/**
 * Initializes the application header by adding various elements.
 */
const initAppHeader = () => {
    initAppLogo();
    try {
        const userData = localStorage.getItem('@jupyterlab/services:UserManager#user');
        if (userData) {
            const user = JSON.parse(userData);
            if (user && user.name) {
                const headerContainerEl = document.createElement('div');
                headerContainerEl.classList.add('ascend-header-container');
                headerContainerEl.id = 'ascend-header-container';
                /** Create the icons */
                const iconsContainerEl = document.createElement('div');
                iconsContainerEl.classList.add('ascend-header-icons');
                if (_configuration__WEBPACK_IMPORTED_MODULE_0__.appConfig.header.getInsulaAppsMenuLinks()) {
                    const icon1 = document.createElement('span');
                    icon1.innerHTML = _icons__WEBPACK_IMPORTED_MODULE_1__.Icons.AppsIcon;
                    icon1.id = 'insulaAppsMenuLinks';
                    icon1.addEventListener('click', () => {
                        showHeaderMenu(_configuration__WEBPACK_IMPORTED_MODULE_0__.appConfig.header.getInsulaAppsMenuLinks(), icon1.id, true);
                    });
                    iconsContainerEl.appendChild(icon1);
                }
                if (_configuration__WEBPACK_IMPORTED_MODULE_0__.appConfig.header.otherInfoMenuLinks) {
                    const icon2 = document.createElement('span');
                    icon2.innerHTML = _icons__WEBPACK_IMPORTED_MODULE_1__.Icons.InfoIcon;
                    icon2.id = 'otherInfoMenuLinks';
                    icon2.addEventListener('click', () => {
                        showHeaderMenu(_configuration__WEBPACK_IMPORTED_MODULE_0__.appConfig.header.otherInfoMenuLinks, icon2.id, false);
                    });
                    iconsContainerEl.appendChild(icon2);
                }
                headerContainerEl.appendChild(iconsContainerEl);
                /** Create the user name panel */
                const userNameContainerEl = document.createElement('div');
                userNameContainerEl.classList.add('ascend-header-user');
                const iconEl = document.createElement('span');
                iconEl.innerHTML = _icons__WEBPACK_IMPORTED_MODULE_1__.Icons.UserIcon;
                const spanEl = document.createElement('span');
                spanEl.innerText = user.name;
                userNameContainerEl.appendChild(iconEl);
                userNameContainerEl.appendChild(spanEl);
                headerContainerEl.appendChild(userNameContainerEl);
                document.body.appendChild(headerContainerEl);
            }
        }
    }
    catch (error) {
        console.error('Error parsing user data:', error);
    }
};
/**
 * Adds a custom logo to the application.
 */
const initAppLogo = () => {
    const imgEl = document.createElement('img');
    imgEl.alt = 'Ascend Logo';
    imgEl.src = _style_logo_png__WEBPACK_IMPORTED_MODULE_4__;
    const logoSectionEL = [
        document.getElementById('jp-MainLogo'),
        document.getElementById('jp-RetroLogo')
    ];
    // Append the logo image and text to each logo section
    logoSectionEL.forEach(el => {
        if (el) {
            el.appendChild(imgEl);
            const spanEl = document.createElement('span');
            spanEl.classList.add('jp-MainLogo-span');
            spanEl.innerHTML = _configuration__WEBPACK_IMPORTED_MODULE_0__.appConfig.appName;
            el.appendChild(spanEl);
        }
    });
};
let currentOpenMenuId = '';
/**
 * Mounts or toggles the visibility of the header menu.
 *
 * @param links - The links to display in the menu.
 * @param id - An ID to identify the menu element.
 * @param avatar - If true, an avatar will be displayed next to each link.
 */
const showHeaderMenu = (links, id, avatar) => {
    const headerMenuContainerId = `ascend-header-menu-container-${id}`;
    let headerMenuContainerEl = document.getElementById(headerMenuContainerId);
    // Hide the currently open menu if it's different from the one being toggled
    if (!!currentOpenMenuId && currentOpenMenuId !== headerMenuContainerId) {
        const currentMenuEl = document.getElementById(currentOpenMenuId);
        if (currentMenuEl) {
            currentMenuEl.style.display = 'none';
        }
    }
    if (headerMenuContainerEl) {
        // Toggle visibility of the existing menu
        if (headerMenuContainerEl.style.display === 'block') {
            headerMenuContainerEl.style.display = 'none';
            currentOpenMenuId = '';
        }
        else {
            headerMenuContainerEl.style.display = 'block';
            currentOpenMenuId = headerMenuContainerId;
        }
    }
    else {
        // Create the menu container if it doesn't exist
        headerMenuContainerEl = document.createElement('div');
        headerMenuContainerEl.id = headerMenuContainerId;
        headerMenuContainerEl.classList.add('ascend-header-menu-container');
        const ulEl = document.createElement('ul');
        ulEl.classList.add('ascend-footer-menu-ul');
        links.forEach(link => {
            const liEl = document.createElement('li');
            const anchorEl = document.createElement('a');
            anchorEl.href = link.href;
            anchorEl.target = '_blank';
            anchorEl.innerText = link.label;
            liEl.appendChild(anchorEl);
            if (avatar) {
                const avatarLetter = link.label.charAt(0).toUpperCase();
                const spanEl = document.createElement('div');
                spanEl.innerText = avatarLetter;
                spanEl.classList.add('ascend-header-menu-avatar');
                anchorEl.before(spanEl);
            }
            ulEl.appendChild(liEl);
        });
        if (id === 'insulaAppsMenuLinks') {
            const paragraphEl = document.createElement('p');
            paragraphEl.innerText = 'Other Applications'.toUpperCase();
            headerMenuContainerEl.appendChild(paragraphEl);
        }
        headerMenuContainerEl.appendChild(ulEl);
        const menuButtonEl = document.getElementById(id);
        if (id === 'insulaAppsMenuLinks' && menuButtonEl) {
            headerMenuContainerEl.style.transform = 'translateX(-350px)';
        }
        menuButtonEl === null || menuButtonEl === void 0 ? void 0 : menuButtonEl.before(headerMenuContainerEl);
        currentOpenMenuId = headerMenuContainerId;
    }
};
document.addEventListener('mouseover', event => {
    var _a;
    if (currentOpenMenuId) {
        const menuDivEl = document.getElementById(currentOpenMenuId);
        if (menuDivEl && menuDivEl.style.display !== 'none') {
            if (!menuDivEl.contains(event.target) &&
                !((_a = document
                    .getElementById('ascend-header-container')) === null || _a === void 0 ? void 0 : _a.contains(event.target))) {
                menuDivEl.style.display = 'none';
                currentOpenMenuId = '';
            }
        }
    }
});


/***/ }),

/***/ "./style/apple-touch-icon.png":
/*!************************************!*\
  !*** ./style/apple-touch-icon.png ***!
  \************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

module.exports = __webpack_require__.p + "0ec523bfe61f21fa95e1.png";

/***/ }),

/***/ "./style/favicon.png":
/*!***************************!*\
  !*** ./style/favicon.png ***!
  \***************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

module.exports = __webpack_require__.p + "0ec523bfe61f21fa95e1.png";

/***/ }),

/***/ "./style/logo.png":
/*!************************!*\
  !*** ./style/logo.png ***!
  \************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

module.exports = __webpack_require__.p + "8c3f1d75af7fe9a5cf2c.png";

/***/ })

}]);
//# sourceMappingURL=lib_index_js.1f65d8183b50d8ac2964.js.map