import { BrowserModule, Title } from '@angular/platform-browser';
import { NgModule, APP_INITIALIZER } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';

// used to create fake backend
import { fakeBackendProvider } from './_helpers';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { HomeComponent } from './home/home.component';
import { TopBarComponent } from './top-bar/top-bar.component';
import { NavBarComponent } from './nav-bar/nav-bar.component';
import { SidebarLeftComponent } from './sidebar-left/sidebar-left.component';
import { SidebarRightComponent } from './sidebar-right/sidebar-right.component';
import { FooterComponent } from './footer/footer.component';
import { AboutUsComponent } from './about-us/about-us.component';
import { ContactComponent } from './contact/contact.component';
import { DownloadComponent } from './download/download.component';
import { HelpComponent } from './help/help.component';
import { PageNotFoundComponent } from './http-errors/page-not-found/page-not-found.component';
import { GenomeViewerComponent } from './genome-viewer/genome-viewer.component';
import { LoginComponent } from './login/login.component';

import { JwtInterceptor, ErrorInterceptor } from './_helpers';
import { ConfigService } from "./config/config.service";
import { BsDropdownModule, TooltipModule, TabsModule, ModalModule } from 'ngx-bootstrap';

// Admin Only
import { AdminHeaderComponent } from './admin/admin-header/admin-header.component';
import { AdminFooterComponent } from './admin/admin-footer/admin-footer.component';
import { DashboardComponent } from './admin/dashboard/dashboard.component';
import { DataUsagePolicyComponent } from './admin/block/data-usage-policy/data-usage-policy.component';
import { NewsComponent } from './admin/block/news/news.component';
import { AboutComponent as AboutBlockComponent } from './admin/block/about/about.component';
import { AboutComponent as AboutPageComponent } from './admin/page/about/about.component';
import { HelpComponent as HelpPageComponent } from './admin/page/help/help.component';
import { BrowserDetailComponent } from './browser-detail/browser-detail.component';
import { NonCodingComponent } from './non-coding/non-coding.component';
import { HelpQaComponent } from './admin/page/help-qa/help-qa.component';
import { ArchiveComponent } from './admin/page/archive/archive.component';
import { ArchiveComponent  as ArchivePageComponent } from './archive/archive.component';
import { TopBarCustomComponent } from './top-bar-custom/top-bar-custom.component';
import { QueryBuilderComponent } from './query-builder/query-builder.component';
import { PrimaryAnnotationComponent } from './query-builder/tabs/primary-annotation/primary-annotation.component';
import { GeneNameComponent } from './query-builder/tabs/gene-name/gene-name.component';
import { GenomeLocationComponent } from './query-builder/tabs/genome-location/genome-location.component';
import { ConservedRegionsComponent } from './query-builder/tabs/conserved-regions/conserved-regions.component';
import { KeggOrthologyIdComponent } from './query-builder/tabs/kegg-orthology-id/kegg-orthology-id.component';
import { ClusterIdComponent, ModalContentComponent1 } from './query-builder/tabs/cluster-id/cluster-id.component';
import { ClusterDescriptionComponent, ModalContentComponent2 } from './query-builder/tabs/cluster-description/cluster-description.component';
import { ProteinDomainComponent } from './query-builder/tabs/protein-domain/protein-domain.component';
import { SecretomeComponent } from './query-builder/tabs/secretome/secretome.component';
import { QueryBuilderFormComponent } from './query-builder/query-builder-form/query-builder-form.component';
import { from } from 'rxjs';
import { VideoTutorialComponent } from './admin/block/video-tutorial/video-tutorial.component';
import { ContactUsComponent } from './admin/page/contact-us/contact-us.component';
import { ScaffoldLinkDetailsComponent } from './browser-detail/scaffold-link-details/scaffold-link-details.component';
import { GffTemplateComponent } from './genome-viewer/gff-template/gff-template.component';

@NgModule({
    declarations: [
        AppComponent,
        HomeComponent,
        TopBarComponent,
        NavBarComponent,
        SidebarLeftComponent,
        SidebarRightComponent,
        FooterComponent,
        AboutUsComponent,
        ContactComponent,
        DownloadComponent,
        HelpComponent,
        PageNotFoundComponent,
        GenomeViewerComponent,
        DashboardComponent,
        LoginComponent,
        AdminHeaderComponent,
        AdminFooterComponent,
        DataUsagePolicyComponent,
        NewsComponent,
        AboutBlockComponent,
        AboutPageComponent,
        HelpPageComponent,
        BrowserDetailComponent,
        NonCodingComponent,
        HelpQaComponent,
        ArchiveComponent,
        ArchivePageComponent,
        TopBarCustomComponent,
        QueryBuilderComponent,
        PrimaryAnnotationComponent,
        GeneNameComponent,
        GenomeLocationComponent,
        ConservedRegionsComponent,
        KeggOrthologyIdComponent,
        ClusterIdComponent,
        ClusterDescriptionComponent,
        ProteinDomainComponent,
        SecretomeComponent,
        QueryBuilderFormComponent,
        ModalContentComponent1,
        ModalContentComponent2,
        VideoTutorialComponent,
        ContactUsComponent,
        ScaffoldLinkDetailsComponent,
        GffTemplateComponent
    ],
    entryComponents: [
        ModalContentComponent1,
        ModalContentComponent2
    ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        HttpClientModule,
        FormsModule,
        ReactiveFormsModule,
        BsDropdownModule.forRoot(),
        TooltipModule.forRoot(),
        TabsModule.forRoot(),
        ModalModule.forRoot()     
    ],
    providers: [
        { provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true },
        { provide: HTTP_INTERCEPTORS, useClass: ErrorInterceptor, multi: true },

        // provider used to create fake backend
        fakeBackendProvider,
        {
            provide: APP_INITIALIZER,
            multi: true,
            deps: [ConfigService],
            useFactory: (appConfigService: ConfigService) => {
                return () => {
                    return appConfigService.loadAppConfig();
                };
            }
        },
        Title
    ],
    bootstrap: [AppComponent]
})
export class AppModule { }
