import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Title } from '@angular/platform-browser';

@Injectable({
    providedIn: 'root'
})
export class ConfigService {

    private appConfig: any;

    constructor(
        private http: HttpClient,
        private titleService: Title
    ) { }

    async loadAppConfig() {
        const data = await this.http.get('/assets/config.json')
            .toPromise();
        this.appConfig = data;
    }

    getSiteName() {
        return 'EUMicrobeDB';
    }

    setPageTitle( pageTitle: string = '' ) {
        this.titleService.setTitle( [ pageTitle, this.getSiteName() ].filter( x => x ).join(' - ') );
    }

    getapiBaseUrl() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.baseUrl;
    }

    getapiTreeUrl() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.treeUrl;
    }

    getapiListUrl() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.listUrl;
    }

    getapiGenomeUrl() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.genomeUrl;
    }

    getBrowserDetailUrl() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.browserDetailUrl;
    }
    
    getScaffoldDetailUrl() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.scaffoldDetailsUrl;
    }

    getBrowserDetailTabUrl() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.browserTabDetailsUrl;
    }

    getNonCodingUrl() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.nonCodingUrl;
    }

    getDataUsagePolicy() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.block.get.dataUsagePolicyUrl;
    }

    setDataUsagePolicy() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.block.post.dataUsagePolicyUrl;
    }

    getNews() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.block.get.newsUrl;
    }

    setNews() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.block.post.newsUrl;
    }

    getAbout() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.block.get.aboutUrl;
    }

    setAbout() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.block.post.aboutUrl;
    }

    getVideoTutorials() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.block.get.videoTutorialsUrl;        
    } 
    
    setVideoTutorials() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.block.post.videoTutorialsUrl;        
    }     

    getAboutPage() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.page.get.aboutUrl;
    }

    setAboutPage() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.page.post.aboutUrl;
    }

    getHelpPage() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.page.get.helpUrl;
    }

    setHelpPage() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.page.post.helpUrl;
    }

    getHelpQAPage() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.page.get.helpQAUrl;
    }

    setHelpQAPage() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.page.post.helpQAUrl;
    }

    getArchivePage() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.page.get.archiveUrl;
    }

    setArchivePage() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.page.post.archiveUrl;
    }

    getContactPage() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.page.get.contactUsUrl;
    }

    setContactPage() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.page.post.contactUsUrl;
    }

    getQueryTabUrl( tabNo: number ) {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.tabs[tabNo];
    }
    
    getProcessQueriesUrl() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.processQueriesUrl;
    }

    getMediaUrl() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.media;
    }

    getBrowserDetailsMediaUrl() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.media.browserDetailsMediaUrl;
    }

    getDNDMediaUrl() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.media.dndMediaUrl;
    }
    
    getGffUploadUrl() {
        if (!this.appConfig) {
            throw Error('Config file not loaded!');
        }

        return this.appConfig.gffUpload;
    }

}
