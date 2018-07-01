import { Component, Inject, OnInit } from '@angular/core';
import { NestedTreeControl } from '@angular/cdk/tree';
import { HttpClient } from '@angular/common/http';
import { MatTreeNestedDataSource } from '@angular/material/tree';
import { Observer, BehaviorSubject } from 'rxjs';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

class Directory {
  // The full path to this directory
  path: string;
  // The name of this directory
  name: string;
  // Whether the subdirectories are loading
  loading: boolean;
  // The children if they have loaded
  children: Array<Directory>;
  // The notifier of the above children
  _children: BehaviorSubject<Array<Directory>>;
}

@Component({
  templateUrl: './directory-picker.component.html',
  styleUrls: ['./directory-picker.component.css']
})
export class DirectoryPickerComponent implements OnInit {

  nestedTreeControl: NestedTreeControl<Directory>;
  nestedDataSource: MatTreeNestedDataSource<Directory>;

  constructor(private http: HttpClient,
              private dialog: MatDialogRef<DirectoryPickerComponent>,
              @Inject(MAT_DIALOG_DATA) private observer: Observer<string>) {
    this.nestedTreeControl = new NestedTreeControl<Directory>(this.getChildren.bind(this));
    this.nestedDataSource = new MatTreeNestedDataSource();
  }

  ngOnInit() {
    let loadChildren = this.loadChildren.bind(this);
    this.nestedTreeControl.expansionModel.onChange.subscribe(change => {
      change.added.forEach((node: Directory) => {
        if (node.loading == true) {
          loadChildren(node);
        }
      });
    });

    let rootNode = new Directory();
    rootNode.path = '';
    rootNode._children = new BehaviorSubject([]);
    rootNode._children.subscribe(roots => this.nestedDataSource.data = roots);
    loadChildren(rootNode);
  }

  hasNestedChild = (_: number, node: Directory) => (node.loading || node.children.length > 0);

  private loadChildren(node: Directory) {
    this.http.get<Array<string>>('/browse' + node.path).subscribe((data: Array<string>) => {
      let directories: Array<Directory> = [];
      data.sort().forEach((name: string) => {
        let directory = new Directory();
        directory.loading = true;
        directory._children = new BehaviorSubject([]);
        directory.path = node.path + '/' + name;
        directory.name = name;
        directories.push(directory);
      });
      node.children = directories;
      node.loading = false;
      node._children.next(node.children);
    }, error => {
      node.children = [];
      node.loading = false;
      node._children.next(node.children);
    });
  }

  private getChildren(node: Directory) {
    return node._children;
  }

  private chooseNode(node: Directory) {
    this.observer.next(node.path);
    this.observer.complete();
    this.dialog.close();
  }

  onNoClick(): void {
    this.dialog.close();
  }

}
