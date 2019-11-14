import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { HomeComponent } from './home/home.component';
import { AboutUsComponent } from './about-us/about-us.component';
import { HelpComponent } from './help/help.component';
import { DownloadComponent } from './download/download.component';
import { ContactComponent } from './contact/contact.component';
import { PageNotFoundComponent } from './http-errors/page-not-found/page-not-found.component';
import { GenomeViewerComponent } from './genome-viewer/genome-viewer.component';
import { LoginComponent } from './login/login.component';
import { AuthGuard } from './_guards';
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
import { QueryBuilderComponent } from './query-builder/query-builder.component';
import { VideoTutorialComponent } from './admin/block/video-tutorial/video-tutorial.component';
import { ContactUsComponent } from './admin/page/contact-us/contact-us.component';
import { ScaffoldLinkDetailsComponent } from './browser-detail/scaffold-link-details/scaffold-link-details.component';
import { GffTemplateComponent } from './genome-viewer/gff-template/gff-template.component';

const routes: Routes = [
    {
        path: '',
        component: HomeComponent
    },
    {
        path: 'about-us',
        component: AboutUsComponent
    },
    {
        path: 'help',
        component: HelpComponent
    },
    {
        path: 'download',
        component: DownloadComponent
    },
    {
        path: 'contact',
        component: ContactComponent
    },
    {
        path: 'archive',
        component: ArchivePageComponent
    },
    {
        path: 'genome-viewer',
        component: GenomeViewerComponent
    },
    {
        path: 'login',
        component: LoginComponent
    },
    {
        path: 'browser-detail',
        component: BrowserDetailComponent
    },
    {
        path: 'query-builder',
        component: QueryBuilderComponent
    },
    {
        path: 'non-coding',
        component: NonCodingComponent
    },
    {
        path: 'scaffold-details',
        component: ScaffoldLinkDetailsComponent
    },
    {
        path: 'gff-template',
        component: GffTemplateComponent
    },
    {
        path: 'admin',
        pathMatch: 'full',
        redirectTo: 'admin/dashboard'
    },
    {
        path: 'admin/dashboard',
        component: DashboardComponent,
        canActivate: [AuthGuard]
    },
    {
        path: 'admin/block/data-usage-policy',
        component: DataUsagePolicyComponent,
        canActivate: [AuthGuard]
    },
    {
        path: 'admin/block/news',
        component: NewsComponent,
        canActivate: [AuthGuard]
    },
    {
        path: 'admin/block/about',
        component: AboutBlockComponent,
        canActivate: [AuthGuard]
    },
    {
        path: 'admin/block/video-tutorials',
        component: VideoTutorialComponent,
        canActivate: [AuthGuard]
    },
    {
        path: 'admin/page/about',
        component: AboutPageComponent,
        canActivate: [AuthGuard]
    },
    {
        path: 'admin/page/help',
        component: HelpPageComponent,
        canActivate: [AuthGuard]
    },
    {
        path: 'admin/page/help-qa',
        component: HelpQaComponent,
        canActivate: [AuthGuard]
    },
    {
        path: 'admin/page/archive',
        component: ArchiveComponent,
        canActivate: [AuthGuard]
    },
    {
        path: 'admin/page/contact-us',
        component: ContactUsComponent,
        canActivate: [AuthGuard]
    },
    { 
        path: '**', 
        component: PageNotFoundComponent 
    },
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule { }
